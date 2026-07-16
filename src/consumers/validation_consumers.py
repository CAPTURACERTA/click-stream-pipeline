import logging
from abc import ABC
from typing import Callable

from ..models import Click, Data, Product, Topics, User
from ..publisher import Publisher
from ..validator import assert_valid_click, assert_valid_product, assert_valid_user

logger = logging.getLogger(__name__)


class ValidationConsumer(ABC):
    event_name: str = ""
    validator: Callable = None
    model: Data = None
    output_topic: Topics = None

    def __init__(self, publisher: Publisher):
        self.publisher = publisher

    async def consume(self, message: str):
        try:
            self.validator(self.model.from_json(message))
        except (TypeError, ValueError) as e:
            logger.warning(
                "Discarding invalid %s event: %s",
                self.event_name,
                e,
            )
        except Exception as e:
            logger.exception(
                "Unexpected error while validating %s event: %s",
                self.event_name,
                e,
            )
        else:
            await self.publisher.publish(
                topic=self.output_topic,
                message=message,
            )


class ClickValidationConsumer(ValidationConsumer):
    event_name = "click"
    validator = assert_valid_click
    model = Click
    output_topic = Topics.CLICKS_VALIDATED.value


class UserValidationConsumer(ValidationConsumer):
    event_name = "user"
    validator = assert_valid_user
    model = User
    output_topic = Topics.USERS_VALIDATED.value


class ProductValidationConsumer(ValidationConsumer):
    event_name = "product"
    validator = assert_valid_product
    model = Product
    output_topic = Topics.PRODUCTS_VALIDATED.value
