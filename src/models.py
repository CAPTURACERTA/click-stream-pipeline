from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from json import dumps, loads
from typing import Protocol

from bson import ObjectId


class Consumer(Protocol):
    async def consume(self, message: str) -> None: ...


class Topics(Enum):
    CLICKS_RAW = "clicks:raw"
    CLICKS_VALIDATED = "clicks:validated"
    USERS_RAW = "users:raw"
    USERS_VALIDATED = "users:validated"
    PRODUCTS_RAW = "products:raw"
    PRODUCTS_VALIDATED = "products:validated"


class Collections(Enum):
    PRODUCTS = "products"
    USERS = "users"
    CLICKS = "clicks"


class Data(ABC):
    @abstractmethod
    def to_dict(self) -> dict:
        pass

    @classmethod
    @abstractmethod
    def from_dict(cls, data: dict):
        pass

    def to_json(self) -> str:
        return dumps(self.to_dict())

    def to_document(self) -> dict:
        """Return a MongoDB-ready document, preserving native BSON-friendly types."""
        return asdict(self)

    @classmethod
    def from_json(cls, json_str: str):
        return cls.from_dict(loads(json_str))


@dataclass(slots=True)
class Click(Data):
    user_id: ObjectId
    product_id: ObjectId
    created_at: datetime
    processed_at: datetime | None = None
    _id: ObjectId = field(default_factory=ObjectId)

    def to_dict(self):
        return {
            "user_id": str(self.user_id),
            "product_id": str(self.product_id),
            "created_at": self.created_at.isoformat(),
            "processed_at": self.processed_at.isoformat()
            if self.processed_at
            else None,
            "_id": str(self._id),
        }

    @classmethod
    def from_dict(cls, data: dict):
        return Click(
            user_id=ObjectId(data["user_id"]),
            product_id=ObjectId(data["product_id"]),
            created_at=datetime.fromisoformat(data["created_at"]),
            processed_at=datetime.fromisoformat(data["processed_at"])
            if data.get("processed_at")
            else None,
            _id=ObjectId(data["_id"]) if data.get("_id") else ObjectId(),
        )


@dataclass(slots=True)
class Product(Data):
    name: str
    price: float | str | None
    _id: ObjectId = field(default_factory=ObjectId)

    def to_dict(self):
        return {"name": self.name, "price": self.price, "_id": str(self._id)}

    @classmethod
    def from_dict(cls, data: dict):
        return Product(
            name=data["name"],
            price=data["price"],
            _id=ObjectId(data["_id"]) if data.get("_id") else ObjectId(),
        )


@dataclass(slots=True)
class User(Data):
    name: str
    _id: ObjectId = field(default_factory=ObjectId)

    def to_dict(self):
        return {"name": self.name, "_id": str(self._id)}

    @classmethod
    def from_dict(cls, data: dict):
        return User(
            name=data["name"],
            _id=ObjectId(data["_id"]) if data.get("_id") else ObjectId(),
        )
