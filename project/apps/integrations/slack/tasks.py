import html
import logging

from celery import shared_task
from django.conf import settings

from .client import SlackClient

logger = logging.getLogger(__name__)


@shared_task
def send_slack_msg(recipient, msg, **kwargs):
    if settings.DEBUG or settings.ENVIRONMENT == 'development':
        logger.info(f'[SEND_SLACK_MSG]: Slack recipient was replaced '
                    f'with test channel "{recipient}" because DEBUG = True')
        msg = f'({settings.ENVIRONMENT}) 🤖 Original channel: {recipient}\n' + msg
        recipient = settings.SLACK_DEV_CHANNEL

    SlackClient().send_msg(recipient, html.unescape(msg), **kwargs)
