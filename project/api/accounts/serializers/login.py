from django.contrib.auth import authenticate, get_user_model
from rest_framework import serializers

from api import messages
from api.serializers import Serializer, ModelSerializer
from apps.accounts import signals
from apps.accounts.models import Token


class LoginSerializer(Serializer):
    password = serializers.CharField(trim_whitespace=False)
    email = serializers.EmailField()

    def validate(self, attrs):
        self.user = authenticate(self._request, username=attrs['email'], password=attrs['password'])

        if not self.user:
            raise serializers.ValidationError(messages.EMAIL_PASSWORD_MISMATCH)

        return attrs

    def save(self, **kwargs):
        token = self.user.login_from_request(self._request, is_endless=True)

        signals.user_logged_in.send(sender=self.user.__class__, request=self._request, response=None, user=self.user)

        return token


class UserSerializer(ModelSerializer):
    name = serializers.CharField()

    class Meta:
        model = get_user_model()
        fields = (
            'id',
            'email',
            'name',
        )
        read_only_fields = ('email',)


class TokenSerializer(ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Token
        fields = ('token', 'user')
