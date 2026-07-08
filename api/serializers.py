from rest_framework import serializers

from orders.models import Order


class PurchaseSerializer(serializers.ModelSerializer):
    address_text = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField(format='%Y-%m-%d %H:%M')
    total_amount = serializers.DecimalField(max_digits=12, decimal_places=2, source='total_amount')

    class Meta:
        model = Order
        fields = ('id', 'total_amount', 'address_text', 'created_at', 'status')

    def get_address_text(self, obj):
        if obj.delivery_address:
            return str(obj.delivery_address)
        # fallback
        primary = getattr(obj.user, 'addresses', None)
        if primary:
            p = primary.filter(is_primary=True).first()
            if p:
                return str(p)
        return ''