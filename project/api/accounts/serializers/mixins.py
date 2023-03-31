from rest_framework import serializers

from api import messages
from api.serializers import Serializer
from apps.accounts.tokens import user_token_generator


class TokenValidationSerializer(Serializer):
    token = serializers.CharField(write_only=True)
    user = None

    def validate_token(self, value):
        if user := user_token_generator.validate_token(value):
            self.user = user
        else:
            raise serializers.ValidationError(messages.TOKEN_INVALID)

        return value
