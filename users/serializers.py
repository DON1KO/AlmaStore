from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
import random

from users.models import *

User = get_user_model()


class VerifyCodeSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=20, required=True)
    code = serializers.CharField(max_length=6, required=True)


class LoginSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=20, required=True)
    password = serializers.CharField(write_only=True, required=True)


class ForgotPasswordSerializer(serializers.Serializer):
    phone_number = serializers.CharField(
        max_length=20,
        required=True,
        help_text="Введите номер телефона для получения кода сброса пароля"
    )


class VerifyResetCodeSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=20, required=True)
    code = serializers.CharField(
        max_length=4,
        required=True,
        help_text="Введите 4-значный код из SMS"
    )


class ResetPasswordSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=20, required=True)
    code = serializers.CharField(max_length=4, required=True)
    new_password = serializers.CharField(
        write_only=True,
        required=True,
        help_text="Введите новый пароль"
    )
    confirm_password = serializers.CharField(
        write_only=True,
        required=True,
        help_text="Повторите новый пароль"
    )

    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"new_password": "Пароли не совпадают"})
        return attrs



class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = '__all__'
        read_only_fields = ('user',)


class BonusCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = BonusCard
        fields = '__all__'

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'


class EmailRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'phone_number', 'password', 'password_confirm', 'first_name', 'last_name']

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password": "Пароли не совпадают"})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User1.objects.create_user(
            email=validated_data['email'],
            phone_number=validated_data.get('phone_number'),
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        UserProfile.objects.create(user=user, first_name=user.first_name, last_name=user.last_name)
        return user