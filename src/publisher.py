from datetime import datetime
from json import dumps

from .broker import MessageBroker
from .models import Click, Topics


class Publisher:
    def __init__(self, broker: MessageBroker):
        self.broker = broker

    async def publish_click(self, click: Click):
        try:
            self._check_click(click)
        except Exception as e:
            print(e)
        else:
            click.published_at = datetime.now().isoformat()
            click = dumps(click)

            target_topic = Topics.CLICKS.value

            await self.broker.publish(target_topic, click)

    @staticmethod
    def _check_click(click: Click): ...
