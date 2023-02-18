import datetime
import logging

import pytz

from utils.tasks import get_object_with_logging
from celeryapp.app import app
from . import emails

logger = logging.getLogger(__name__)


@app.task
def send_email_confirmation(*, user_id):
    emails.send_email_confirmation(user_id=user_id)


@app.task
def send_password_reset_email(*, user_id, next_url=''):
    emails.send_password_reset_email(user_id=user_id, next_url=next_url)


@app.task
def update_last_used_at(token_id, timestamp):
    from apps.accounts.models import Token

    token = get_object_with_logging(Token, token_id)

    if token is not None:
        try:
            date = datetime.datetime.fromtimestamp(timestamp, tz=pytz.UTC)
        except TypeError as e:
            return logger.exception(e)

        token.update_last_used(date)


@app.task
def send_magic_link(*, user_id, next_url=''):
    emails.send_magic_link(user_id=user_id, next_url=next_url)
