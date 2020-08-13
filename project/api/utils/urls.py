from rest_framework.routers import DefaultRouter

from api.utils.viewsets import UtilsViewSet

app_name = 'utils'

router = DefaultRouter()
router.register('', UtilsViewSet, 'utils')

urlpatterns = router.urls
