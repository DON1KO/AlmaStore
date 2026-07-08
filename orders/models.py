from django.db import models
from users.models import User1
from shop.models import Product

class Address(models.Model):
    user = models.ForeignKey(User1, on_delete=models.CASCADE, related_name='addresses')
    street = models.CharField(max_length=200)
    house = models.CharField(max_length=10)
    building = models.CharField(max_length=10, blank=True)
    entrance = models.CharField(max_length=10, blank=True)
    floor = models.CharField(max_length=10, blank=True)
    is_primary = models.BooleanField(default=False)

    class Meta:
        db_table = 'addresses'
        verbose_name_plural = 'Addresses'

    def __str__(self):
        return f"{self.street}, {self.house}"


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Ожидает подтверждения'),
        ('confirmed', 'Подтвержден'),
        ('preparing', 'Готовится'),
        ('delivering', 'Доставляется'),
        ('completed', 'Завершен'),
        ('cancelled', 'Отменен'),
    ]

    PAYMENT_METHODS = [
        ('cash', 'Наличными'),
        ('card', 'Картой'),
    ]

    DELIVERY_TIME_CHOICES = [
        ('asap', 'Как можно быстрее'),
        ('schedule', 'Выбрать дату и время'),
    ]

    user = models.ForeignKey(User1, on_delete=models.CASCADE, related_name='orders')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    delivery_address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, blank=True)
    delivery_time_option = models.CharField(max_length=20, choices=DELIVERY_TIME_CHOICES, default='asap')
    scheduled_delivery_time = models.DateTimeField(null=True, blank=True)
    comment = models.TextField(blank=True)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, default='cash')
    order_amount = models.DecimalField(max_digits=10, decimal_places=2)
    delivery_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        self.total_amount = self.order_amount + self.delivery_fee
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Order #{self.id} - {self.user}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = 'order_items'
