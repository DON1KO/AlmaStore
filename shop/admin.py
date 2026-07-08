from django.contrib import admin
from shop.models import *


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'order')

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price')

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('address', 'working_hours')


admin.site.register(Promotion)

admin.site.register(Favorite)
