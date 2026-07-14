from .broker import MessageBroker


class Publisher:
    def __init__(self, broker: MessageBroker):
        self.broker = broker

    async def publish(self, topic: str, message: str):
        await self.broker.publish(topic, message)
