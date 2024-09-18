from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Product, Shop, Category, ProductInfo, Parameter, ProductParameter, Order, OrderItem, Contact


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']
        read_only_fields = ['id']


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ['id', 'user', 'type', 'phone', 'city', 'street', 'house', 'structure', 'building', 'apartment']
        read_only_fields = ['id', 'user']


class ShopSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shop
        fields = ['id', 'name', 'url', 'state']
        read_only_fields = ['id']


class ShopOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shop
        fields = ['name', 'url']


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', ]
        read_only_fields = ['id']


class ProductSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(read_only=True, slug_field='name')
    class Meta:
        model = Product
        fields = ['id', 'name', 'category']
        read_only_fields = ['id']


class ProductOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['name']


class ParameterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Parameter
        fields = ['id', 'name']
        read_only_fields = ['id']


class ProductParameterListingFields(serializers.RelatedField):
    def to_representation(self, value):
        return f'{value.parameter}: {value.value}'


class ProductInfoSerializer(serializers.ModelSerializer):
    product = ProductSerializer()
    shop = ShopSerializer()
    product_parameters = ProductParameterListingFields(queryset=ProductParameter.objects.all(), many=True)

    class Meta:
        model = ProductInfo
        fields = ['product', 'model', 'product_parameters', 'quantity', 'price', 'price_rrc', 'shop']


class ProductInfoOrderSerializer(serializers.ModelSerializer):
    product = ProductOrderSerializer()

    class Meta:
        model = ProductInfo
        fields = ['id', 'product', 'price_rrc']


class OrderItemSerializer(serializers.ModelSerializer):
    product_info = ProductInfoOrderSerializer()
    shop = ShopOrderSerializer()

    class Meta:
        model = OrderItem
        fields = ['product_info', 'quantity', 'shop']
        read_only_fields = ['shop']


class OrderDetailSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True)
    total_sum = serializers.IntegerField()
    class Meta:
        model = Order
        fields = ('id', 'order_items', 'status', 'dt', 'total_sum')
        read_only_fields = ('id',)


class OrderSerializer(serializers.ModelSerializer):
    total_sum = serializers.IntegerField()

    class Meta:
        model = Order
        fields = ('id', 'status', 'dt', 'total_sum')
        read_only_fields = ('id',)
