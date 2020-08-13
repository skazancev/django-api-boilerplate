from django.contrib.auth import get_user_model
from django.utils.http import base36_to_int

from django.contrib.auth.tokens import PasswordResetTokenGenerator


class UserTokenGenerator(PasswordResetTokenGenerator):
    def get_object(self, uidb36):
        user_model = get_user_model()

        try:
            return user_model.objects.get(pk=base36_to_int(uidb36))
        except (ValueError, user_model.DoesNotExist):
            return None


user_token_generator = UserTokenGenerator()
