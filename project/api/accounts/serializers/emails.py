from api.serializers import Serializer
from apps.accounts import signals
from .mixins import TokenSerializer


class EmailConfirmSerializer(TokenSerializer, Serializer):
    user = None

    def save(self, **kwargs):
        self.user.is_email_verified = True
        self.user.save()

        signals.email_confirmed.send(
            sender=self.user.__class__,
            request=self._request,
            user=self.user
        )

        return self.user
