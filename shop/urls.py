from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, ProductViewSet, PromotionViewSet, LocationViewSet, FavoriteViewSet

router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'products', ProductViewSet)
router.register(r'promotions', PromotionViewSet)
router.register(r'locations', LocationViewSet)
router.register(r'favorites', FavoriteViewSet, basename='favorites')

urlpatterns = router.urls
