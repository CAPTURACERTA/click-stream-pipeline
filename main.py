import asyncio
import logging
from collections.abc import Iterable

from src.broker import MessageBroker
from src.config_log import setup_logging
from src.consumers.mongo import Mongo, MongoConsumer
from src.consumers.redis import Redis, RedisConsumer
from src.consumers.validation_consumers import (
    ClickValidationConsumer,
    ProductValidationConsumer,
    UserValidationConsumer,
)
from src.generator import generate_clicks, generate_products, generate_users
from src.models import Click, Collections, Data, Product, Topics, User
from src.publisher import Publisher

setup_logging()
logger = logging.getLogger(__name__)


async def publish_events(
    publisher: Publisher, topic: Topics, events: Iterable[Data]
) -> None:
    events = list(events)
    await asyncio.gather(
        *(publisher.publish(topic.value, event.to_json()) for event in events)
    )
    logger.info("Published %d events to '%s'.", len(events), topic.value)


def configure_consumers(
    broker: MessageBroker, publisher: Publisher, mongo: Mongo, redis: Redis
) -> None:
    """Wire raw-event validation to the validated storage and metrics consumers."""
    broker.subscribe(Topics.USERS_RAW.value, UserValidationConsumer(publisher))
    broker.subscribe(Topics.PRODUCTS_RAW.value, ProductValidationConsumer(publisher))
    broker.subscribe(Topics.CLICKS_RAW.value, ClickValidationConsumer(publisher))

    broker.subscribe(
        Topics.USERS_VALIDATED.value,
        MongoConsumer(mongo, Collections.USERS.value, User),
    )
    broker.subscribe(
        Topics.PRODUCTS_VALIDATED.value,
        MongoConsumer(mongo, Collections.PRODUCTS.value, Product),
    )
    broker.subscribe(
        Topics.CLICKS_VALIDATED.value,
        MongoConsumer(mongo, Collections.CLICKS.value, Click),
    )
    broker.subscribe(Topics.CLICKS_VALIDATED.value, RedisConsumer(redis))


async def run_pipeline() -> None:
    logger.info("--- INITIALIZING DATA PIPELINE ---")
    broker = MessageBroker()
    publisher = Publisher(broker)
    mongo = Mongo()
    redis = Redis()
    configure_consumers(broker, publisher, mongo, redis)

    try:
        users = generate_users(15)
        products = generate_products(10)
        clicks = generate_clicks(50, products, users)

        # Persist dimensions before the click stream, preserving event ordering at the stage level.
        await publish_events(publisher, Topics.USERS_RAW, users)
        await publish_events(publisher, Topics.PRODUCTS_RAW, products)
        await broker.drain()

        await publish_events(publisher, Topics.CLICKS_RAW, clicks)
        await broker.drain()
        logger.info("--- PIPELINE SUCCESSFULLY COMPLETED ---")
    finally:
        await broker.close()
        await mongo.close()
        await redis.close()


if __name__ == "__main__":
    asyncio.run(run_pipeline())
