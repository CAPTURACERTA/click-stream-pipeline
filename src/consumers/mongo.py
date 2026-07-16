import logging
from json import loads

from pymongo.asynchronous.mongo_client import AsyncMongoClient

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

    async def insert_one(self, collection: str, data: dict):
        await self.db[collection].insert_one(data)


class MongoConsumer:
    """Consumer class for MongoDB.\n
    Consumes products, users and clicks"""

    def __init__(self, mongo: Mongo, collection: str):
        self.mongo = mongo
        self.collection = collection

    async def consume(self, message: str) -> None:
        data = loads(message)
        await self.mongo.insert_one(self.collection, data)
