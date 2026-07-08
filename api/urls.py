from django.urls import path, include
from rest_framework.routers import DefaultRouter

from api.views import *
from cart.views import *
from orders.views import *
from shop.views import *
from users.views import *

router = DefaultRouter()
router.register(r'home', HomeViewSet, basename='home')
router.register(r'purchases', PurchasesViewSet, basename='purchases')
router.register(r'categories', CategoryViewSet)
router.register(r'products', ProductViewSet)
router.register(r'cart', CartViewSet, basename='cart')
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'addresses', AddressViewSet, basename='address')
router.register(r'locations', LocationViewSet)
router.register(r'favorites', FavoriteViewSet, basename='favorites')
router.register(r'bonus-cards', BonusCardViewSet, basename='bonuscard')
router.register(r'notifications', NotificationViewSet, basename='notification')
router.register(r'promotions', PromotionViewSet)


urlpatterns = [
    path('', include(router.urls)),
    # include apps routers so final endpoints keep same paths:
    path('', include('shop.urls')),     # /categories/, /products/, /promotions/, /favorites/
    path('', include('cart.urls')),     # /cart/
    path('', include('orders.urls')),   # /orders/, /addresses/
    path('', include('users.urls')),
]