import html
import logging

from django.conf import settings

from apps.bots.clients import slack_client
from celeryapp.app import app

logger = logging.getLogger(__name__)


@app.task
def send_slack_msg(recipient, msg, **kwargs):
    if not settings.SLACK_ENABLED:
        return

    if settings.DEBUG or settings.ENVIRONMENT == 'development':
        logger.info(f'[SEND_SLACK_MSG]: Slack recipient was replaced '
                    f'with test channel "{recipient}" because DEBUG = True')
        msg = f'({settings.ENVIRONMENT}) 🤖 Original channel: {recipient}\n' + msg
        recipient = settings.SLACK_DEV_CHANNEL

    slack_client.send_msg(recipient, html.unescape(msg), **kwargs)
