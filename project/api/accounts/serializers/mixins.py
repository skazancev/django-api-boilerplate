from rest_framework import serializers

from api import messages
from api.serializers import Serializer
from apps.accounts.tokens import user_token_generator


class TokenValidationSerializer(Serializer):
    token = serializers.CharField(write_only=True)
    user = None

    def validate_token(self, value, one_off=True):
        if user := user_token_generator.validate_token(value, one_off=one_off):
            self.user = user
        else:
            raise serializers.ValidationError(messages.TOKEN_INVALID)

        return value
