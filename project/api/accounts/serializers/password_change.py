from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from api import messages
from api.serializers import Serializer


class PasswordChangeSerializer(Serializer):
    old_password = serializers.CharField(trim_whitespace=False)
    new_password = serializers.CharField(trim_whitespace=False)

    def validate_old_password(self, old_password):
        if not self._user.check_password(old_password):
            raise serializers.ValidationError(messages.PASSWORD_INCORRECT)

        return old_password

    def validate_new_password(self, new_password):
        validate_password(password=new_password, user=self._user)

        return new_password

    def save(self):
        self._user.change_password(self.validated_data['new_password'])

        return self._user
