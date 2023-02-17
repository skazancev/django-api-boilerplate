from rest_framework.routers import DefaultRouter

from api.accounts.viewsets import AccountsViewSet, AuthViewSet, PasswordAuthViewSet

app_name = 'accounts'

router = DefaultRouter()
router.register('', AccountsViewSet, 'accounts')
router.register('auth', AuthViewSet, 'auth')
router.register('auth/password', PasswordAuthViewSet, 'password_auth')

urlpatterns = router.urls
