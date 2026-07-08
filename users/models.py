import random

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils import timezone
from datetime import timedelta
from django.conf import settings

class UserManager(BaseUserManager):
    def create_user(self, email, phone_number=None, password=None, **extra_fields):
        if not email:
            raise ValueError('Email должен быть указан')
        email = self.normalize_email(email)
        user = self.model(email=email, phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        return self.create_user(email, password=password, **extra_fields)

class User(AbstractUser):
    username = None
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True, unique=True)
    is_phone_verified = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()


class UserProfile(models.Model):
    GENDER_CHOICES = [('male','Мужской'), ('female','Женский')]
    MARITAL_STATUS_CHOICES = [('single','Холост/Не замужем'), ('married','Женат/Замужем'),
                              ('divorced','Разведен(а)'), ('widowed','Вдовец/Вдова')]
    SOCIAL_STATUS_CHOICES = [('student','Студент'), ('working','Работающий'),
                             ('unemployed','Безработный'), ('retired','Пенсионер')]
    LANGUAGE_CHOICES = [('russian','Русский'), ('kyrgyz','Кыргызский')]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    birth_date = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True)
    native_language = models.CharField(max_length=20, choices=LANGUAGE_CHOICES, blank=True)
    marital_status = models.CharField(max_length=20, choices=MARITAL_STATUS_CHOICES, blank=True)
    social_status = models.CharField(max_length=20, choices=SOCIAL_STATUS_CHOICES, blank=True)
    city = models.CharField(max_length=100, blank=True)
    has_home = models.BooleanField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class SMSVerification(models.Model):
    phone_number = models.CharField(max_length=20)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    class Meta:
        db_table = 'sms_verifications'


class BonusCard(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='bonus_card')
    card_number = models.CharField(max_length=16, unique=True)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'bonus_cards'

    def __str__(self):
        return f"Card {self.card_number}"


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']

    def __str__(self):
        return self.title

User1 = get_user_model()

class OTP(models.Model):
    user = models.ForeignKey(User1, on_delete=models.CASCADE, related_name='otps')
    code = models.CharField(max_length=6, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = f"{random.randint(100000, 999999)}"  # Генерация 6-значного кода
        super().save(*args, **kwargs)