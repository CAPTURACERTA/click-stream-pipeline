import logging
from pymongo.asynchronous.mongo_client import AsyncMongoClient

from ..models import Data

URI = "mongodb://localhost:27017/"
DB_NAME = "e-commerce"


logger = logging.getLogger(__name__)


class Mongo:
    """Database class for Mongodb"""

    def __init__(self, uri: str = URI, db_name: str = DB_NAME):
        self.uri = uri
        self.name = db_name
        self.client = AsyncMongoClient(uri)
        self.db = self.client[db_name]

    async def close(self):
        await self.client.aclose()
        logger.info("MongoDB connection closed.")

    async def insert_one(self, collection: str, data: dict):
        await self.db[collection].insert_one(data)
        logger.debug("Inserted document into MongoDB collection '%s'.", collection)


class MongoConsumer:
    """Consumer class for MongoDB.\n
    Consumes products, users and clicks"""

    def __init__(self, mongo: Mongo, collection: str, model: type[Data]):
        self.mongo = mongo
        self.collection = collection
        self.model = model

    async def consume(self, message: str) -> None:
        data = self.model.from_json(message).to_document()
        await self.mongo.insert_one(self.collection, data)
        logger.debug("Persisted %s event in MongoDB.", self.model.__name__)
