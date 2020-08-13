from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

from rest_framework import serializers

from api import messages
from apps.accounts import signals
from apps.accounts.tasks import send_password_reset_email
from .mixins import TokenSerializer
from ...serializers import Serializer


class PasswordResetSerializer(Serializer):
    email = serializers.EmailField()

    def validate_email(self, email):
        self.user = get_user_model().objects.filter(email=email).first()
        if not self.user:
            raise serializers.ValidationError(messages.EMAIL_NOT_ASSIGNED)

        return email

    def save(self):
        send_password_reset_email.delay(user_id=self.user.id, next_url=self._request.GET.get('next'))

        return self.user


class PasswordResetConfirmSerializer(TokenSerializer):
    password = serializers.CharField(trim_whitespace=False, write_only=True)

    def validate_password(self, password):
        validate_password(password, user=self.user)

        return password

    def save(self, **kwargs):
        self.user.set_password(self.validated_data['password'])
        self.user.is_email_verified = True
        self.user.save()

        signals.password_reset.send(sender=self.user.__class__, request=self._request, user=self.user)
        signals.email_confirmed.send(sender=self.user.__class__, request=self._request, user=self.user)

        return self.user
