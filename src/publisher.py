import logging

from .broker import MessageBroker

logger = logging.getLogger(__name__)


class Publisher:
    def __init__(self, broker: MessageBroker):
        self.broker = broker

    async def publish(self, topic: str, message: str) -> None:
        await self.broker.publish(topic, message)
        logger.debug("Published event to '%s'.", topic)
