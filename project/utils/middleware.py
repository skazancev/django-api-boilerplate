from django.contrib.auth import get_user_model
from django.contrib.auth.middleware import AuthenticationMiddleware


class CustomAuthenticationMiddleware(AuthenticationMiddleware):
    def process_request(self, request):
        super().process_request(request)
        if request.GET.get('debug_user') and request.user.is_authenticated and request.user.is_superuser:
            if debug_user := get_user_model().objects.filter(id=request.GET.get('debug_user')).last():
                request.original_user, request.user = request.user, debug_user
