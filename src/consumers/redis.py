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
        logger.info("Redis connection closed.")

    async def register_click(self, product_id: str, user_id: str) -> None:
        """Apply all click metrics atomically."""
        async with self.client.pipeline(transaction=True) as pipeline:
            pipeline.hincrby(f"products:{product_id}", "views", 1)
            pipeline.hincrby(f"users:{user_id}", "clicks", 1)
            pipeline.zincrby("products:rank:views", 1, product_id)
            await pipeline.execute()


class RedisConsumer:
    """Consumer class for Redis\n
    Consumes clicks only"""

    def __init__(self, redis: Redis):
        self.redis = redis

    async def consume(self, message: str):
        click = loads(message)

        await self.redis.register_click(click["product_id"], click["user_id"])
        logger.debug("Updated Redis metrics for click '%s'.", click.get("_id"))
