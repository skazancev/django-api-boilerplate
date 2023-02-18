import logging
import re

from api.webhooks.clients.base import BaseClient

logger = logging.getLogger(__name__)


class SlackBotClient(BaseClient):
    def process_type(self):
        return self.content.type

    def interactive_message(self):
        for callback in callbacks:
            if match := callback.match(self.content['callback_id']):
                return callback(self.content, **match.groupdict()).process()


callbacks = []
