from django.contrib.auth import get_user_model
from django.contrib.auth import password_validation
from rest_framework import serializers

from api.serializers import ModelSerializer
from apps.accounts import signals
from apps.accounts.tasks import send_email_confirmation


class SignUpSerializer(ModelSerializer):
    email = serializers.EmailField()

    class Meta:
        model = get_user_model()
        fields = ('email', 'password', 'first_name', 'last_name')
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def save(self):
        self.user = get_user_model().objects.create_user(
            **self.validated_data,
            is_active=True,
        )

        send_email_confirmation.delay(user_id=self.user.id)
        signals.user_signed_up.send(sender=self.user.__class__, request=self._request, user=self.user)

        return self.create_token()

    def create_token(self):
        return self.user.create_login_token_from_request(self._request, is_endless=True)

    def validate_password(self, password):
        password_validation.validate_password(password)

        return password

    def validate_email(self, value):
        if get_user_model().objects.filter(email=value).exists():
            raise serializers.ValidationError(_('Пользователь с таким адресом эл. почты уже существует.'))

        return value
