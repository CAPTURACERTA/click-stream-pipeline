import asyncio
import logging
from contextlib import suppress

from .models import Consumer

logger = logging.getLogger(__name__)


class MessageBroker:
    def __init__(self):
        self.queues: dict[str, asyncio.Queue] = {}
        self.listeners: dict[str, list[Consumer]] = {}
        self._dispatcher_tasks: dict[str, asyncio.Task[None]] = {}
        self._processing_failures: list[Exception] = []
        self._closed = False

    def subscribe(self, topic: str, consumer: Consumer) -> None:
        if self._closed:
            raise RuntimeError("Cannot subscribe to a closed broker.")

        listeners = self.listeners.setdefault(topic, [])
        if consumer in listeners:
            logger.warning("Consumer already subscribed to topic '%s'.", topic)
            return

        listeners.append(consumer)
        logger.info("Subscribed %s to topic '%s'.", type(consumer).__name__, topic)

    async def publish(self, topic: str, message: str) -> None:
        if self._closed:
            raise RuntimeError("Cannot publish to a closed broker.")
        if not isinstance(message, str):
            raise TypeError("Broker messages must be JSON strings.")

        if topic not in self.queues:
            self.queues[topic] = asyncio.Queue()
            self._dispatcher_tasks[topic] = asyncio.create_task(
                self._start_dispatcher(topic), name=f"dispatcher:{topic}"
            )

        await self.queues[topic].put(message)
        logger.debug("Published message to topic '%s'.", topic)

    async def drain(self) -> None:
        """Wait until all messages currently queued have been consumed."""
        while True:
            queues = list(self.queues.values())
            await asyncio.gather(*(queue.join() for queue in queues))
            # A consumer can publish to a topic after its queue was joined.
            if all(queue.empty() for queue in self.queues.values()):
                if self._processing_failures:
                    failures, self._processing_failures = self._processing_failures, []
                    raise RuntimeError(
                        f"{len(failures)} consumer(s) failed while processing messages."
                    ) from failures[0]
                return

    async def close(self) -> None:
        if self._closed:
            return

        try:
            await self.drain()
        finally:
            self._closed = True
            for task in self._dispatcher_tasks.values():
                task.cancel()
            for task in self._dispatcher_tasks.values():
                with suppress(asyncio.CancelledError):
                    await task
            logger.info("Message broker closed.")

    async def _start_dispatcher(self, topic: str):
        queue = self.queues[topic]

        while True:
            message = await queue.get()

            try:
                consumers = self.listeners.get(topic, [])
                if not consumers:
                    logger.warning("No consumers subscribed to topic '%s'.", topic)
                    continue

                results = await asyncio.gather(
                    *(consumer.consume(message) for consumer in consumers),
                    return_exceptions=True,
                )
                for consumer, result in zip(consumers, results, strict=True):
                    if isinstance(result, Exception):
                        self._processing_failures.append(result)
                        logger.exception(
                            "Consumer %s failed while processing topic '%s'.",
                            type(consumer).__name__,
                            topic,
                            exc_info=result,
                        )
            finally:
                queue.task_done()
