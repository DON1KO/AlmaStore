from rest_framework import serializers
from .models import Address, Order, OrderItem
from shop.serializers import ProductSerializer

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = '__all__'

class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    class Meta:
        model = OrderItem
        fields = '__all__'

class OrderCreateSerializer(serializers.ModelSerializer):
    delivery_address_id = serializers.IntegerField(write_only=True)
    total_amount = serializers.ReadOnlyField()
    class Meta:
        model = Order
        fields = ['delivery_address_id','delivery_time_option','scheduled_delivery_time','comment','payment_method','order_amount','delivery_fee','total_amount']
    def validate_delivery_address_id(self, value):
        user = self.context['request'].user
        if not Address.objects.filter(id=value, user=user).exists():
            raise serializers.ValidationError("Адрес не найден")
        return value

class OrderListSerializer(serializers.ModelSerializer):
    delivery_address = AddressSerializer(read_only=True)
    items = OrderItemSerializer(many=True, read_only=True)
    class Meta:
        model = Order
        fields = '__all__'
