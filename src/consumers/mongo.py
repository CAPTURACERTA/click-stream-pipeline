from json import loads

from mongo_config import DB_NAME, URI
from pymongo.asynchronous.mongo_client import AsyncMongoClient

from ..models import Collections


class Mongo:
    def __init__(self, uri: str = URI, db_name: str = DB_NAME):
        self.uri = uri
        self.name = db_name
        self.client = AsyncMongoClient(uri)
        self.db = self.client[db_name]

    def close(self):
        self.client.close()

    async def insert_one(self, collection: str, data: dict):
        await self.db[collection].insert_one(data)


class MongoConsumer:
    def __init__(self, mongo: Mongo, collection: Collections):
        self.mongo = mongo
        self.collection = collection

    async def consume(self, message: str) -> None:
        data = loads(message)
        await self.mongo.insert_one(self.collection, data)
