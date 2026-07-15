import logging
from datetime import datetime

from bson import ObjectId

from .models import Click, Product, User

logger = logging.getLogger(__name__)


def _validate_object_id(value: ObjectId, field_name: str) -> None:
    if not isinstance(value, ObjectId):
        logger.error("%s must be a valid ObjectId.", field_name)
        raise TypeError(f"{field_name} must be a valid ObjectId.")


def _validate_datetime(
    value: datetime | None,
    field_name: str,
    *,
    allow_none: bool = False,
) -> None:
    if value is None:
        if allow_none:
            return

        logger.error("%s cannot be None.", field_name)
        raise ValueError(f"{field_name} cannot be None.")

    if not isinstance(value, datetime):
        logger.error("%s must be a datetime.", field_name)
        raise TypeError(f"{field_name} must be a datetime.")


def _validate_non_empty_string(value: str, field_name: str) -> None:
    if not isinstance(value, str):
        logger.error("%s must be a string.", field_name)
        raise TypeError(f"{field_name} must be a string.")

    if not value.strip():
        logger.error("%s cannot be empty.", field_name)
        raise ValueError(f"{field_name} cannot be empty.")


def assert_valid_user(user: User) -> None:
    if not isinstance(user, User):
        logger.error("Expected User instance.")
        raise TypeError("Expected User instance.")

    _validate_object_id(user._id, "_id")
    _validate_non_empty_string(user.name, "name")


def assert_valid_product(product: Product) -> None:
    if not isinstance(product, Product):
        logger.error("Expected Product instance.")
        raise TypeError("Expected Product instance.")

    _validate_object_id(product._id, "_id")
    _validate_non_empty_string(product.name, "name")

    if not isinstance(product.price, (int, float)):
        logger.error("price must be numeric.")
        raise TypeError("price must be numeric.")

    if product.price < 0:
        logger.error("price cannot be negative.")
        raise ValueError("price cannot be negative.")


def assert_valid_click(click: Click) -> None:
    if not isinstance(click, Click):
        logger.error("Expected Click instance.")
        raise TypeError("Expected Click instance.")

    _validate_object_id(click._id, "_id")
    _validate_object_id(click.user_id, "user_id")
    _validate_object_id(click.product_id, "product_id")

    _validate_datetime(click.created_at, "created_at")
    _validate_datetime(click.processed_at, "processed_at", allow_none=True)

    if (
        click.processed_at is not None
        and click.created_at is not None
        and click.processed_at < click.created_at
    ):
        logger.error("processed_at cannot be earlier than created_at.")
        raise ValueError("processed_at cannot be earlier than created_at.")
