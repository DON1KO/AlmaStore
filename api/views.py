import base64
from io import BytesIO
import qrcode
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from orders.models import Order
from orders.serializers import OrderListSerializer
from shop.models import Category, Promotion
from shop.serializers import PromotionSerializer



class HomeViewSet(ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        # --- MENU ---
        menu_items = []
        for c in Category.objects.all()[:10]:
            menu_items.append({
                "id": c.id,
                "title": c.name,
                "image": request.build_absolute_uri(c.image.url) if c.image else None
            })

        # --- QR ---
        user = request.user
        if user.is_authenticated:
            data = f"user:{user.id}"
            bonus = getattr(user.bonus_card, "balance", 0) if hasattr(user, "bonus_card") else 0
            card_number = getattr(user.bonus_card, "card_number", None) if hasattr(user, "bonus_card") else None
        else:
            data = "guest"
            bonus = 0
            card_number = None

        qr = qrcode.make(data)
        buf = BytesIO()
        qr.save(buf, format='PNG')
        qr_base64 = base64.b64encode(buf.getvalue()).decode()

        # --- PROMOTIONS ---
        promotions = Promotion.objects.filter(is_active=True)
        promotions_data = PromotionSerializer(promotions, many=True, context={"request": request}).data


        return Response({
            "bonus": bonus,
            "card_number": card_number,
            "qr_code": qr_base64,
            "promotions": promotions_data,
            "menu": menu_items
        })



class PurchasesViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        orders = Order.objects.filter(user=request.user).order_by('-created_at')
        return Response(OrderListSerializer(orders, many=True, context={'request': request}).data)