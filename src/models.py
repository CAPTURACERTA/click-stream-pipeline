from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from json import dumps, loads
from typing import Protocol

from bson import ObjectId


class Consumer(Protocol):
    async def consume(self, message: str) -> None: ...


class Topics(Enum):
    CLICKS = "clicks"
    USERS = "users"
    PRODUCTS = "products"


class Collections(Enum):
    PRODUCTS = "products"
    USERS = "users"
    CLICKS = "clicks"


@dataclass(slots=True)
class Click:
    user_id: ObjectId
    product_id: ObjectId
    timestamp: datetime
    published_at: datetime = field(default_factory=None)
    processed_at: datetime = field(default_factory=None)
    _id: ObjectId = field(default_factory=ObjectId)

    def to_dict(self):
        return {
            "user_id": str(self.user_id),
            "product_id": str(self.product_id),
            "timestamp": self.timestamp.isoformat(),
            "published_at": self.published_at.isoformat()
            if self.published_at
            else None,
            "processed_at": self.processed_at.isoformat()
            if self.processed_at
            else None,
            "_id": str(self._id),
        }

    def to_json(self):
        return dumps(self.to_dict())

    @classmethod
    def from_dict(cls, data: dict):
        return Click(
            user_id=ObjectId(data["user_id"]),
            product_id=ObjectId(data["product_id"]),
            timestamp=datetime.fromisoformat(data["timestamp"]),
            published_at=datetime.fromisoformat(data["published_at"])
            if data.get("published_at")
            else None,
            processed_at=datetime.fromisoformat(data["processed_at"])
            if data.get("processed_at")
            else None,
            _id=ObjectId(data["_id"]) if data.get("_id") else ObjectId(),
        )

    @classmethod
    def from_json(cls, json_str: str):
        data = loads(json_str)
        return cls.from_dict(data)


@dataclass(slots=True)
class Product:
    name: str
    price: float
    _id: ObjectId = field(default_factory=ObjectId)

    def to_dict(self):
        return {"name": self.name, "price": self.price, "_id": str(self._id)}

    def to_json(self):
        return dumps(self.to_dict())

    @classmethod
    def from_dict(cls, data: dict):
        return Product(
            name=data["name"],
            price=data["price"],
            _id=ObjectId(data["_id"]) if data.get("_id") else ObjectId(),
        )

    @classmethod
    def from_json(cls, json_str: str):
        data = loads(json_str)
        return cls.from_dict(data)


@dataclass(slots=True)
class User:
    name: str
    _id: ObjectId = field(default_factory=ObjectId)

    def to_dict(self):
        return {"name": self.name, "_id": str(self._id)}

    def to_json(self):
        return dumps(self.to_dict())

    @classmethod
    def from_dict(cls, data: dict):
        return User(
            name=data["name"],
            _id=ObjectId(data["_id"]) if data.get("_id") else ObjectId(),
        )

    @classmethod
    def from_json(cls, json_str: str):
        data = loads(json_str)
        return cls.from_dict(data)
