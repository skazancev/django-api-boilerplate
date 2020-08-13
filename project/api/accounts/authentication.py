from django.utils import timezone
from rest_framework import exceptions
from rest_framework.authentication import TokenAuthentication as BaseTokenAuthentication
from rest_framework.exceptions import AuthenticationFailed

from api import messages
from apps.accounts.models import Token
from apps.accounts.tasks import update_last_used_at


class TokenAuthentication(BaseTokenAuthentication):
    model = Token

    def authenticate_credentials(self, key):
        try:
            token_user, token = super().authenticate_credentials(self.model.token2key(key))
        except (AuthenticationFailed, ValueError):
            raise exceptions.AuthenticationFailed(messages.TOKEN_INVALID)

        if token.has_expired():
            return None

        update_last_used_at.delay(token_id=token.id, timestamp=timezone.now().timestamp())

        return token_user, token
