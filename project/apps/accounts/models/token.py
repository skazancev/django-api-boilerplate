import base64
import logging
from binascii import hexlify, unhexlify
from math import ceil
from secrets import token_hex

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models, IntegrityError
from django.utils import timezone

from utils.models import BaseModel

logger = logging.getLogger(__name__)


class Token(BaseModel):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)

    key = models.CharField(max_length=40, unique=True)
    user_agent = models.CharField(max_length=250)
    ip_address = models.GenericIPAddressField(unpack_ipv4=True)
    is_endless = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    last_used_at = models.DateTimeField(auto_now_add=True)

    @property
    def token(self):
        return self.key2token(self.key)

    @classmethod
    def token2key(cls, token):
        return hexlify(base64.urlsafe_b64decode(token.ljust(ceil(len(token) / 4) * 4, '='))).decode()

    @classmethod
    def key2token(cls, key):
        return base64.urlsafe_b64encode(unhexlify(key)).decode().strip('=')

    @classmethod
    def create(cls, user, is_endless=False, ip_address='', user_agent=''):
        attempts = 10
        while True:
            try:
                return cls.objects.create(
                    user=user,
                    key=token_hex(20),
                    ip_address=ip_address,
                    is_endless=is_endless,
                    user_agent=user_agent
                )
            except IntegrityError:
                if attempts > 0:
                    attempts -= 1
                else:
                    raise

    def has_expired(self):
        if self.is_endless:
            return False

        return self.last_used_at + settings.LOGIN_TOKEN_EXPIRATION_TIME <= timezone.now()

    def update_last_used(self, date):
        self.last_used_at = date
        self.save()

    def str(self):
        return f'{self.key} for user={self.user_id}'
