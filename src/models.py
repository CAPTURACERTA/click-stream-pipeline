from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from bson import ObjectId


class Topics(Enum):
    CLICKS = "clicks"
    USERS = "users"
    PRODUCTS = "products"


@dataclass(slots=True)
class Click:
    user_id: ObjectId
    product_id: ObjectId
    timestamp: datetime
    created_at: datetime
    processed_at: datetime
