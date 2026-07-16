import logging
from json import loads

import redis.asyncio as redis

logger = logging.getLogger(__name__)


class Redis:
    """Database class for Redis"""

    def __init__(self, uri: str = "redis://localhost:6379", db: int = 0):
        self.uri = uri
        self.db_index = db
        self.client = redis.from_url(
            uri, db=db, encoding="utf-8", decode_responses=True
        )

    async def close(self):
        await self.client.aclose()

    async def incr_product_views(self, product_id: str):
        await self.client.hincrby(f"products:{product_id}", "views", 1)

    async def incr_user_clicks(self, user_id: str):
        await self.client.hincrby(f"users:{user_id}", "clicks", 1)

    async def incr_product_rank(self, product_id: str):
        await self.client.zincrby("products:rank:views", 1, product_id)


class RedisConsumer:
    """Consumer class for Redis\n
    Consumes clicks only"""

    def __init__(self, redis: Redis):
        self.redis = redis

    async def consume(self, message: str):
        click = loads(message)

        await self.redis.incr_product_views(click["product_id"])
        await self.redis.incr_user_clicks(click["user_id"])
        await self.redis.incr_product_rank(click["product_id"])
