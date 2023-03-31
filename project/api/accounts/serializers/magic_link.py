from django.contrib.auth import get_user_model
from django.contrib.auth import login as django_login
from rest_framework import serializers

from api import messages
from api.accounts.serializers.mixins import TokenValidationSerializer
from api.serializers import Serializer
from apps.accounts import signals
from apps.accounts.tasks import send_magic_link
from apps.communication.models import CommunicationHistory, Template

User = get_user_model()


class MagicLinkSerializer(TokenValidationSerializer):
    def validate_token(self, value):
        return super().validate_token(value)

    def save(self, **kwargs):
        if admin_user := self._request.GET.get('admin_user'):
            if User.objects.filter(id=admin_user, is_staff=True).first():
                django_login(self._request, self.user)
                return self.user

        self.user.is_email_verified = True
        self.user.save()

        signals.email_confirmed.send(sender=self.user.__class__, request=self._request, user=self.user)
        self.user.login_from_request(self._request)

        return self.user


class MagicLinkSendSerializer(Serializer):
    email = serializers.EmailField()

    def validate_email(self, email):
        self.user = User.objects.filter(email=email).first()
        if not self.user:
            raise serializers.ValidationError(messages.EMAIL_NOT_ASSIGNED)

        return email

    def validate(self, attrs):
        if not CommunicationHistory.can_be_sent(
            template_type=Template.Types.accounts_password_reset_magic_link,
            user_id=self.user.id
        ):
            raise serializers.ValidationError(_('Magic Link уже отправлен.'))

        return attrs

    def save(self, **kwargs):
        send_magic_link.delay(user_id=self.user.id, next_url=self._request.GET.get('next'))
