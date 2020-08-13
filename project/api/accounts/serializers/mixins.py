from rest_framework import serializers

from api import messages
from api.serializers import Serializer
from apps.accounts.tokens import user_token_generator


class TokenSerializer(Serializer):
    token = serializers.CharField(write_only=True)
    user = None

    def validate_token(self, value):
        try:
            uidb36, token = value.split('-', maxsplit=1)
        except ValueError:
            raise serializers.ValidationError(messages.TOKEN_INVALID)

        self.user = user_token_generator.get_object(uidb36)

        if not self.user:
            raise serializers.ValidationError(messages.TOKEN_INVALID)

        if not user_token_generator.check_token(user=self.user, token=token):
            raise serializers.ValidationError(messages.TOKEN_INVALID)

        return value
