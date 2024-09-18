from django.contrib import admin
from .models import Contact, Parameter, Category, Product, ProductInfo, ProductParameter, Shop, Order, OrderItem


@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    list_display = ['name', 'url', 'owner']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', ]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category']


@admin.register(ProductInfo)
class ProductInfoAdmin(admin.ModelAdmin):
    list_display = ['product', 'shop', 'model', 'quantity', 'price', 'price_rrc']


@admin.register(Parameter)
class ParameterAdmin(admin.ModelAdmin):
    list_display = ['name',]


@admin.register(ProductParameter)
class ProductParameterAdmin(admin.ModelAdmin):
    list_display = ['product_info', 'parameter', 'value']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['user', 'dt', 'status']


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product_info', 'shop', 'quantity']


# @admin.register(Contact)
# class ContactAdmin(admin.ModelAdmin):
#     list_display = ['user', 'type', 'phone', 'city', 'street', 'house', 'structure', 'building', 'apartment']
