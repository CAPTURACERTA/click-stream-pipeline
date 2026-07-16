import asyncio
from datetime import datetime, timezone

import pytest

from src.broker import MessageBroker
from src.consumers.validation_consumers import ProductValidationConsumer
from src.models import Click, Product, User
from src.publisher import Publisher
from src.utils import simulate_latency
from src.validator import assert_valid_click, assert_valid_product, assert_valid_user


class CapturingPublisher:
    def __init__(self) -> None:
        self.messages: list[tuple[str, str]] = []

    async def publish(self, topic: str, message: str) -> None:
        self.messages.append((topic, message))


class RecordingConsumer:
    def __init__(self) -> None:
        self.messages: list[str] = []

    async def consume(self, message: str) -> None:
        self.messages.append(message)


class FailingConsumer:
    async def consume(self, message: str) -> None:
        raise ConnectionError("database unavailable")


def test_click_round_trip_preserves_bson_friendly_values() -> None:
    user = User("Ada Lovelace")
    product = Product("Mechanical keyboard", 199.9)
    click = Click(user._id, product._id, datetime.now(timezone.utc))

    restored_click = Click.from_json(click.to_json())

    assert restored_click.to_document()["_id"] == click._id
    assert restored_click.to_document()["user_id"] == user._id
    assert isinstance(restored_click.to_document()["created_at"], datetime)


def test_valid_models_are_accepted() -> None:
    user = User("Grace Hopper")
    product = Product("Monitor", 899.0)
    click = Click(user._id, product._id, datetime.now(timezone.utc))

    assert_valid_user(user)
    assert_valid_product(product)
    assert_valid_click(click)


def test_invalid_product_price_is_rejected() -> None:
    with pytest.raises(TypeError, match="price must be numeric"):
        assert_valid_product(Product("Monitor", "free"))


def test_broker_delivers_all_published_messages() -> None:
    async def scenario() -> None:
        broker = MessageBroker()
        consumer = RecordingConsumer()
        broker.subscribe("test", consumer)
        publisher = Publisher(broker)

        await asyncio.gather(
            *(publisher.publish("test", str(value)) for value in range(10))
        )
        await broker.drain()
        await broker.close()

        assert sorted(consumer.messages, key=int) == [str(i) for i in range(10)]

    asyncio.run(scenario())


def test_broker_surfaces_consumer_failures() -> None:
    async def scenario() -> None:
        broker = MessageBroker()
        broker.subscribe("test", FailingConsumer())
        await broker.publish("test", "event")

        with pytest.raises(RuntimeError, match="1 consumer"):
            await broker.drain()
        await broker.close()

    asyncio.run(scenario())


def test_invalid_event_is_not_forwarded() -> None:
    async def scenario() -> None:
        publisher = CapturingPublisher()
        consumer = ProductValidationConsumer(publisher)

        await consumer.consume(Product("Mouse", 50.0).to_json())
        await consumer.consume(Product("Mouse", "not-available").to_json())

        assert len(publisher.messages) == 1

    asyncio.run(scenario())


def test_latency_decorator_supports_async_functions() -> None:
    async def scenario() -> None:
        calls: list[str] = []

        @simulate_latency(chance=1, min_seconds=0, max_seconds=0)
        async def operation() -> str:
            calls.append("done")
            return "result"

        assert await operation() == "result"
        assert calls == ["done"]

    asyncio.run(scenario())
