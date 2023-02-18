from django.contrib.auth import get_user_model
from django.utils.http import base36_to_int

from django.contrib.auth.tokens import PasswordResetTokenGenerator

from utils.core import override_attribute


class UserTokenGenerator(PasswordResetTokenGenerator):
    # make support custom exp token
    def get_object(self, uidb36):
        user_model = get_user_model()

        try:
            return user_model.objects.get(pk=base36_to_int(uidb36))
        except (ValueError, user_model.DoesNotExist):
            return None

    def validate_token(self, token, one_off=True):
        try:
            uidb36, token = token.split('-', maxsplit=1)
        except ValueError:
            return False

        user = self.get_object(uidb36)

        if not user:
            return False

        setattr(user, '_one_off', one_off)
        if not self.check_token(user=user, token=token):
            return False

        return user

    def _make_hash_value(self, user, timestamp):
        with override_attribute(user, 'last_login', None, apply=getattr('user', '_one_off', True)):
            return super()._make_hash_value(user, timestamp)

    def make_token(self, user, one_off=True):
        with override_attribute(user, 'last_login', None, apply=one_off):
            return super().make_token(user)


user_token_generator = UserTokenGenerator()
