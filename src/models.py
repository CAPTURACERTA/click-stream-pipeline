from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Protocol

from bson import ObjectId


class Consumer(Protocol):
    async def consume(self, message: str) -> None: ...


class Topics(Enum):
    CLICKS = "clicks"
    USERS = "users"
    PRODUCTS = "products"


@dataclass(slots=True)
class Click:
    user_id: ObjectId
    product_id: ObjectId
    timestamp: datetime
    published_at: datetime = field(default_factory=None)
    processed_at: datetime = field(default_factory=None)
    _id: ObjectId = field(default_factory=ObjectId)


@dataclass(slots=True)
class Product:
    name: str
    price: float
    _id: ObjectId = field(default_factory=ObjectId)


@dataclass(slots=True)
class User:
    name: str
    _id: ObjectId = field(default_factory=ObjectId)
