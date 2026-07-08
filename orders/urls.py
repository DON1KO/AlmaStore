from rest_framework.routers import DefaultRouter
from .views import OrderViewSet, AddressViewSet

router = DefaultRouter()
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'addresses', AddressViewSet, basename='address')

urlpatterns = router.urls
