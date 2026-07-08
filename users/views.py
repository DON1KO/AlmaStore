from rest_framework import permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import CreateAPIView
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .serializers import *
import os
import qrcode
from rest_framework.viewsets import ViewSet
from rest_framework.permissions import IsAuthenticated
from .models import BonusCard, Notification
from rest_framework import generics, status
from rest_framework.response import Response
from .serializers import EmailRegisterSerializer
from django.core.mail import send_mail
import requests
from django.conf import settings
import logging
logger = logging.getLogger(__name__)



class RegisterAPIView(APIView):
    """
    GET  -> показывает форму (DRF Browsable API)
    POST -> регистрирует пользователя, создаёт OTP, отправляет код на email (+ OneSignal, если настроен)
    """
    def get(self, request):
        # возвращаем пустой сериализатор — DRF покажет форму
        serializer = EmailRegisterSerializer()
        return Response(serializer.data)

    def post(self, request):
        serializer = EmailRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Создаём запись OTP (код генерируется в модели)
        otp_obj = OTP.objects.create(user=user)

        # Отправка email с кодом (Gmail)
        try:
            send_mail(
                subject="Код подтверждения",
                message=f"Ваш код подтверждения: {otp_obj.code}",
                from_email=getattr(settings, "DEFAULT_FROM_EMAIL", settings.EMAIL_HOST_USER),
                recipient_list=[user.email],
                fail_silently=False,
            )
        except Exception as e:
            # не падаем полностью — возвращаем предупреждение в ответе и логируем
            logger.exception("Ошибка отправки email с OTP: %s", e)
            # возвращаем успешное создание, но с предупреждением
            return Response({
                "detail": "Пользователь создан, но отправка email не удалась. Проверь настройки SMTP.",
                "email_error": str(e),
                "user": {
                    "email": user.email,
                    "phone_number": user.phone_number,
                }
            }, status=status.HTTP_201_CREATED)

        # Отправка push через OneSignal (если настроен)
        if getattr(settings, "ONESIGNAL_APP_ID", None) and getattr(settings, "ONESIGNAL_API_KEY", None):
            try:
                onesignal_url = "https://onesignal.com/api/v1/notifications"
                headers = {
                    "Content-Type": "application/json; charset=utf-8",
                    "Authorization": f"Basic {settings.ONESIGNAL_API_KEY}"
                }
                payload = {
                    "app_id": settings.ONESIGNAL_APP_ID,
                    # лучше указывать реальные идентификаторы устройства (player ids).
                    # Для теста мы используем include_email_tokens, но убедись, что
                    # в OneSignal настроены email tokens для этого пользователя.
                    "include_email_tokens": [user.email],
                    "headings": {"en": "Код подтверждения"},
                    "contents": {"en": f"Ваш код: {otp_obj.code}"}
                }
                requests.post(onesignal_url, json=payload, headers=headers, timeout=10)
            except Exception as e:
                logger.exception("OneSignal send error: %s", e)
                # OneSignal — необязателен, не прерываем регистрацию

        # Успешный ответ
        return Response({
            "detail": "Пользователь создан, код отправлен на email.",
            "user": {
                "email": user.email,
                "phone_number": user.phone_number,
            }
        }, status=status.HTTP_201_CREATED)
class VerifyCodeView(generics.CreateAPIView):
    serializer_class = VerifyCodeSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone_number = serializer.validated_data['phone_number']
        code = serializer.validated_data['code']

        try:
            verification = SMSVerification.objects.filter(
                phone_number=phone_number,
                code=code,
                is_used=False
            ).latest('created_at')

            user = User1.objects.get(phone_number=phone_number)
            user.is_phone_verified = True
            user.save()

            card_number = ''.join([str(random.randint(0, 9)) for _ in range(16)])
            BonusCard.objects.create(user=user, card_number=card_number)

            verification.is_used = True
            verification.save()

            refresh = RefreshToken.for_user(user)

            return Response({
                'message': 'Карта успешно создана! Теперь вы можете экономить на покупках.',
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': {
                    'id': user.id,
                    'phone_number': user.phone_number,
                    'first_name': user.first_name,
                    'last_name': user.last_name
                }
            })

        except SMSVerification.DoesNotExist:
            return Response({'error': 'Неверный код'}, status=status.HTTP_400_BAD_REQUEST)
        except User1.DoesNotExist:
            return Response({'error': 'Пользователь не найден'}, status=status.HTTP_404_NOT_FOUND)


class LoginView(generics.CreateAPIView):
    serializer_class = LoginSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone_number = serializer.validated_data['phone_number']
        password = serializer.validated_data['password']

        user = authenticate(phone_number=phone_number, password=password)

        if user:
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': {
                    'id': user.id,
                    'phone_number': user.phone_number,
                    'first_name': user.first_name,
                    'last_name': user.last_name
                }
            })

        return Response({'error': 'Неверный номер или пароль'}, status=status.HTTP_401_UNAUTHORIZED)


class ForgotPasswordView(generics.CreateAPIView):
    """1. Этап: Ввод номера телефона для получения кода"""
    serializer_class = ForgotPasswordSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone_number = serializer.validated_data['phone_number']

        try:
            User1.objects.get(phone_number=phone_number)

            # Генерируем 4-значный код
            code = ''.join([str(random.randint(0, 9)) for _ in range(4)])
            SMSVerification.objects.create(phone_number=phone_number, code=code)

            print(f"Код для сброса пароля для {phone_number}: {code}")

            return Response({
                'message': 'Код отправлен на ваш номер телефона',
                'reset_code': code,  # В реальном проекте убрать!
                'next_step': 'Используйте этот код для подтверждения в /api/auth/verify-reset-code/'
            })

        except User1.DoesNotExist:
            return Response({'error': 'Пользователь с таким номером не найден'},
                            status=status.HTTP_404_NOT_FOUND)


class VerifyResetCodeView(generics.CreateAPIView):
    """2. Этап: Подтверждение кода из SMS"""
    serializer_class = VerifyResetCodeSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone_number = serializer.validated_data['phone_number']
        code = serializer.validated_data['code']

        try:
            verification = SMSVerification.objects.filter(
                phone_number=phone_number,
                code=code,
                is_used=False
            ).latest('created_at')

            # Помечаем код как использованный для сброса пароля
            verification.is_used = True
            verification.save()

            return Response({
                'message': 'Код подтвержден успешно',
                'next_step': 'Теперь вы можете установить новый пароль в /api/auth/reset-password/'
            })

        except SMSVerification.DoesNotExist:
            return Response({'error': 'Неверный код'}, status=status.HTTP_400_BAD_REQUEST)


class ResetPasswordView(generics.CreateAPIView):
    """3. Этап: Установка нового пароля"""
    serializer_class = ResetPasswordSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone_number = serializer.validated_data['phone_number']
        code = serializer.validated_data['code']
        new_password = serializer.validated_data['new_password']

        try:
            # Проверяем что код был использован на предыдущем этапе
            SMSVerification.objects.filter(
                phone_number=phone_number,
                code=code,
                is_used=True
            ).latest('created_at')

            user = User1.objects.get(phone_number=phone_number)
            user.set_password(new_password)
            user.save()

            return Response({'message': 'Пароль успешно изменен'})

        except SMSVerification.DoesNotExist:
            return Response({'error': 'Сначала подтвердите код через /api/auth/verify-reset-code/'},
                            status=status.HTTP_400_BAD_REQUEST)
        except User1.DoesNotExist:
            return Response({'error': 'Пользователь не найден'}, status=status.HTTP_404_NOT_FOUND)

class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        profile, created = UserProfile.objects.get_or_create(user=self.request.user)
        return profile


# Оставляем старый profile view для обратной совместимости
@api_view(['GET', 'PUT'])
@permission_classes([permissions.IsAuthenticated])
def profile(request):
    """Профиль пользователя (старая версия)"""
    if request.method == 'GET':
        profile = request.user.profile
        serializer = UserProfileSerializer(profile)
        return Response(serializer.data)

    elif request.method == 'PUT':
        profile = request.user.profile
        serializer = UserProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    return None


class BonusCardViewSet(ViewSet):
    permission_classes = [IsAuthenticated]
    def list(self, request):
        card = getattr(request.user, 'bonus_card', None)
        if not card:
            return Response({'bonus':0, 'qr_code_url': None})
        # генерируем png в MEDIA_ROOT/qr_codes/
        rel_path = f"qr_codes/bonus_{card.card_number}.png"
        abs_path = os.path.join(settings.MEDIA_ROOT, rel_path)
        if not os.path.exists(abs_path):
            os.makedirs(os.path.dirname(abs_path), exist_ok=True)
            img = qrcode.make(card.card_number)
            img.save(abs_path)
        qr_url = request.build_absolute_uri(settings.MEDIA_URL + rel_path)
        return Response({'bonus': float(card.balance), 'card_number': card.card_number, 'qr_code_url': qr_url})

class NotificationViewSet(ViewSet):
    permission_classes = [IsAuthenticated]
    def list(self, request):
        qs = Notification.objects.filter(user=request.user)
        return Response(NotificationSerializer(qs, many=True, context={'request': request}).data)


