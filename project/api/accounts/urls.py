from rest_framework.routers import DefaultRouter

from api.accounts.viewsets import AccountsViewSet

app_name = 'accounts'

router = DefaultRouter()
router.register('', AccountsViewSet, 'accounts')

urlpatterns = router.urls
