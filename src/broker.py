import asyncio
import logging

from .models import Consumer

logger = logging.getLogger(__name__)


class MessageBroker:
    def __init__(self):
        self.queues: dict[str, asyncio.Queue] = {}
        self.listeners: dict[str, list[Consumer]] = {}
        self._dispatcher_tasks: list[asyncio.Task] = []

    def subscribe(self, topic: str, consumer: Consumer):
        if topic not in self.listeners:
            self.listeners[topic] = []
        self.listeners[topic].append(consumer)

    async def publish(self, topic: str, message: str):
        if topic not in self.queues:
            self.queues[topic] = asyncio.Queue()
            task = asyncio.create_task(self._start_dispatcher(topic))
            self._dispatcher_tasks.append(task)

        await self.queues[topic].put(message)

    async def _start_dispatcher(self, topic: str):
        queue = self.queues[topic]

        while True:
            message = await queue.get()

            if topic in self.listeners:
                for consumer in self.listeners[topic]:
                    asyncio.create_task(consumer.consume(message))

            queue.task_done()
