import re

from django.contrib.auth import get_user_model
from django.utils.http import base36_to_int

from django.contrib.auth.tokens import PasswordResetTokenGenerator

from utils.core import override_attribute


class UserTokenGenerator(PasswordResetTokenGenerator):
    one_off_postfix = '-o'
    token_re = re.compile(r'^(?P<uidb36>\w+)-(?P<token>[\w-]+?)(?P<one_off>-o)?$')

    def get_object(self, uidb36):
        user_model = get_user_model()

        try:
            return user_model.objects.get(pk=base36_to_int(uidb36))
        except (ValueError, user_model.DoesNotExist):
            return None

    def validate_token(self, token):
        try:
            match = self.token_re.match(token).groupdict()
            uidb36 = match['uidb36']
            token = match['token']
            one_off = match['one_off'] == self.one_off_postfix
        except AttributeError:
            return False

        user = self.get_object(uidb36)

        # set attribute not to override whole methods _make_hash_value and make_token
        setattr(user, '_one_off', one_off)
        if not self.check_token(user=user, token=token):
            return False

        return user

    def _make_hash_value(self, user, timestamp):
        last_login = user.last_login if getattr(user, '_one_off', False) else None
        with override_attribute(user, 'last_login', last_login):
            return super()._make_hash_value(user, timestamp)

    def make_token(self, user, one_off=True):
        last_login = user.last_login if one_off else None
        with override_attribute(user, 'last_login', last_login):
            token = super().make_token(user)

        if one_off:
            token += self.one_off_postfix

        return token


user_token_generator = UserTokenGenerator()
