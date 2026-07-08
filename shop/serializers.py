from rest_framework import serializers
from .models import Category, Product, Promotion, Location, Favorite

class CategorySerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    class Meta:
        model = Category
        fields = '__all__'
    def get_image_url(self, obj):
        req = self.context.get('request')
        if obj.image and req:
            return req.build_absolute_uri(obj.image.url)
        return obj.image.url if obj.image else None

class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    image_url = serializers.SerializerMethodField()
    class Meta:
        model = Product
        fields = '__all__'
    def get_image_url(self, obj):
        req = self.context.get('request')
        if obj.image and req:
            return req.build_absolute_uri(obj.image.url)
        return obj.image.url if obj.image else None

class PromotionSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    class Meta:
        model = Promotion
        fields = '__all__'
    def get_image_url(self, obj):
        req = self.context.get('request')
        if obj.image and req:
            return req.build_absolute_uri(obj.image.url)
        return obj.image.url if obj.image else None

class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = '__all__'

class FavoriteSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.IntegerField(write_only=True, required=False)
    class Meta:
        model = Favorite
        fields = '__all__'
    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user
        product_id = validated_data.pop('product_id', None) or request.data.get('product') or request.data.get('product_id')
        if not product_id:
            raise serializers.ValidationError({'product_id': 'This field is required.'})
        product = Product.objects.get(id=product_id)
        fav, created = Favorite.objects.get_or_create(user=user, product=product)
        return fav
