from rest_framework import viewsets, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Address, Order
from .serializers import AddressSerializer, OrderCreateSerializer, OrderListSerializer

class AddressViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Только для чтения — GET
    """
    serializer_class = AddressSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)

class OrderViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin):
    permission_classes = [IsAuthenticated]
    def get_serializer_class(self):
        if self.action == 'create_order':
            return OrderCreateSerializer
        return OrderListSerializer
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)
    @action(detail=False, methods=['post'])
    def create_order(self, request):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        delivery_address = Address.objects.get(id=serializer.validated_data['delivery_address_id'], user=request.user)
        order = Order.objects.create(
            user=request.user,
            delivery_address=delivery_address,
            delivery_time_option=serializer.validated_data['delivery_time_option'],
            scheduled_delivery_time=serializer.validated_data.get('scheduled_delivery_time'),
            comment=serializer.validated_data.get('comment',''),
            payment_method=serializer.validated_data['payment_method'],
            order_amount=serializer.validated_data['order_amount'],
            delivery_fee=serializer.validated_data['delivery_fee']
        )
        return Response({'message':'Заказ успешно оформлен','order': OrderListSerializer(order, context={'request': request}).data}, status=201)
