from rest_framework.routers import DefaultRouter

from api.accounts.viewsets import AccountsViewSet, AuthViewSet, PasswordAuthViewSet, MagicLinkAuthViewSet

app_name = 'accounts'

router = DefaultRouter()
router.register('', AccountsViewSet, 'accounts')
router.register('auth', AuthViewSet, 'auth')
router.register('auth/password', PasswordAuthViewSet, 'password_auth')
router.register('auth/magic-link', MagicLinkAuthViewSet, 'password_magic_link')

urlpatterns = router.urls
