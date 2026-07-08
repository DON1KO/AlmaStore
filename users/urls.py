from django.urls import path, include
from .views import *
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'bonus-cards', BonusCardViewSet, basename='bonuscard')
router.register(r'notifications', NotificationViewSet, basename='notification')


urlpatterns = [
    path('', include(router.urls)),
    path('register/', RegisterAPIView.as_view(), name='register'),
    path('verify-code/', VerifyCodeView.as_view(), name='verify_code'),
    path('login/', LoginView.as_view(), name='login'),
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot_password'),  # 1. Ввод номера
    path('verify-reset-code/', VerifyResetCodeView.as_view(), name='verify_reset_code'),  # 2. Ввод кода
    path('reset-password/', ResetPasswordView.as_view(), name='reset_password'),  # 3. Новый пароль
    path('profile/', profile, name='profile'),
]