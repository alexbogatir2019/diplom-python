from django.contrib.auth import authenticate, login, logout
from django.core.exceptions import ObjectDoesNotExist
from django.db.utils import IntegrityError
from django.db.models import Sum, F
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from django.contrib.auth.models import User
from rest_framework.response import Response
import yaml
from backend.models import Product, Shop, Category, Order, Contact, OrderItem, ProductInfo, Parameter, ProductParameter
from backend.serializers import ShopSerializer, CategorySerializer, OrderSerializer, \
    ProductInfoSerializer, ParameterSerializer, OrderDetailSerializer, ContactSerializer, OrderItemSerializer, \
    UserSerializer
from backend.tasks import send_email_order_confirm, send_email_registration


class UserRegistrationView(APIView):

    def post(self, request):
        """
            Регистрация нового пользователя
        """

        try:
            user = User.objects.create(**request.data)
            serializer = UserSerializer(user, data=request.data)
            serializer.is_valid(raise_exception=True)
            user.set_password(request.data.get('password'))
            serializer.save()
        except IntegrityError:
            return Response({'status': 'Пользователь с таким именем уже существует'})

        if user.email is not None:
            send_email_registration(user.id)
        return Response({'status': 'Пользователь создан успешно'})

    def patch(self, request):
        """
            Изменение данных пользователя
        """
        if not request.user.is_authenticated:
            return Response({'status': 'Аутентификация не пройдена'})
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'status': 'Пользователь изменен'})


class LoginView(APIView):
    """
        Аутентификация пользователя
    """

    def post(self, request):
        user = authenticate(**request.data)
        if user and user.is_active:
            login(request, user)
            return Response({'status': 'Аутентификация пройдена', 'Пользователь': user.username})
        else:
            return Response({'status': 'Аутентификация не пройдена'})


class LogoutView(APIView):
    """
        Выход пользователя
    """

    def post(self, request):
        logout(request)
        return Response({'status': 'Выход выполнен'})


class ContactView(APIView):
    """
        Заполнение контактной информации
    """

    def post(self, request):
        if not request.user.is_authenticated:
            return Response({'status': 'Аутентификация не пройдена'})
        contact = Contact.objects.create(user=request.user, **request.data)
        contact.save()
        return Response({'status': 'Контактная информация заполнена'})

    def get(self, request):
        if not request.user.is_authenticated:
            return Response({'status': 'Аутентификация не пройдена'})
        contact = Contact.objects.get(user=request.user)
        serializer = ContactSerializer(contact)
        return Response(serializer.data)

    def patch(self, request):
        if not request.user.is_authenticated:
            return Response({'status': 'Аутентификация не пройдена'})
        contact = Contact.objects.get(user=request.user)
        serializer = ContactSerializer(contact, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'status': 'Контактная информация изменена'})

    def delete(self, request):
        if not request.user.is_authenticated:
            return Response({'status': 'Аутентификация не пройдена'})
        contact = Contact.objects.get(user=request.user)
        contact.delete()
        return Response({'status': 'Контактная информация удалена'})


class ShopViewSet(ModelViewSet):
    queryset = Shop.objects.all()
    serializer_class = ShopSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filterset_fields = ['name']


class CategoryViewSet(ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filterset_fields = ['name', 'shops']


class ProductViewSet(ModelViewSet):
    serializer_class = ProductInfoSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    queryset = ProductInfo.objects.all().select_related('product', 'shop')
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['product', 'model', 'product_parameters', 'shop']
    search_fields = ['product', 'model', 'product_parameters', 'shop', 'quantity', 'price', 'price_rrc']


class ParameterViewSet(ModelViewSet):
    queryset = Parameter.objects.all()
    serializer_class = ParameterSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class BasketView(APIView):
    """
        Добавление и удаление товаров из корзины
    """

    permission_classes = [IsAuthenticated]

    def put(self, request):
        """ Добавление товара в корзину """

        if request.user.contact.type != 'BUYER':
            return Response({'status': 'Только покупатели могут добавлять товары в корзину'})

        basket, _ = Order.objects.get_or_create(user=request.user, status='BASKET')
        product = Product.objects.get(id=request.data.get('product_id'))
        shop = ProductInfo.objects.get(id=product.id).shop
        product_info = ProductInfo.objects.get(product=product)
        quantity = request.data.get('quantity')

        OrderItem.objects.create(order=basket, product_info=product_info, shop=shop, quantity=quantity)
        return Response({'status': 'Товар добавлен в корзину'})

    def get(self, request):
        """ Просмотр содержимого корзины """

        if request.user.contact.type != 'BUYER':
            return Response({'status': 'Только для покупателей!'})

        basket = Order.objects.filter(
            user_id=request.user.id, status='BASKET').prefetch_related(
            'order_items__product_info__product__category',
            'order_items__product_info__product_parameters__parameter').annotate(
            total_sum=Sum(F('order_items__quantity') * F('order_items__product_info__price_rrc'))).distinct()
        serializer = OrderDetailSerializer(basket, many=True)
        return Response(serializer.data)

    def patch(self, request):
        """
            Изменение количества товара в корзине
        """

        if request.user.contact.type != 'BUYER':
            return Response({'status': 'Только для покупателей!'})

        try:
            order_item = OrderItem.objects.get(order__user=request.user, order__status='BASKET',
                                               product_info__product=request.data.get('product_id'))
            serializer = OrderItemSerializer(order_item, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({'status': 'Количество товара изменено'})
        except ObjectDoesNotExist:
            return Response({'status': 'Указанный товар отсутствует в корзине'}, status=404)

    def delete(self, request):
        """
            Удаление товара из корзины
        """

        if request.user.contact.type != 'BUYER':
            return Response({'status': 'Только для покупателей!'})

        try:
            order_item = OrderItem.objects.get(order__user=request.user, order__status='BASKET',
                                               product_info__product=request.data.get('product_id'))
            order_item.delete()
            return Response({'status': 'Товар удален из корзины'})
        except ObjectDoesNotExist:
            return Response({'status': 'Указанный товар отсутствует в корзине'}, status=404)



class SupplierUpdate(APIView):
    """Загрузка информации о магазине, категориях товаров, товарах, характеристиках."""
    permission_classes = [IsAuthenticated]

    def post(self, request, file_name):

        if request.user.contact.type != 'SHOP':
            return Response({'status': 'Загрузка доступна только магазину'})

        with open(f'{file_name}', 'r', encoding='UTF-8') as f:
            data = yaml.safe_load(f)
            shop, _ = Shop.objects.get_or_create(name=data['shop'], owner=request.user.contact)
            for category in data['categories']:
                category_object, _ = Category.objects.get_or_create(id=category['id'], name=category['name'])
                category_object.shops.add(shop.id)
                category_object.save()
            for item in data['goods']:
                product, _ = Product.objects.get_or_create(name=item['name'], category_id=item['category'])
                product_info = ProductInfo.objects.create(product_id=product.id,
                                                          shop_id=shop.id,
                                                          model=item['model'],
                                                          quantity=item['quantity'],
                                                          price=item['price'],
                                                          price_rrc=item['price_rrc'])
                for key, value in item['parameters'].items():
                    parameter_object, _ = Parameter.objects.get_or_create(name=key)
                    ProductParameter.objects.create(product_info_id=product_info.id,
                                                    parameter_id=parameter_object.id,
                                                    value=value)
        return Response({'status': 'products added successfully'})


class OrderViewSet(ModelViewSet):
    """
        Просмотр информации о заказах
    """
    queryset = Order.objects.annotate(
        total_sum=Sum(F('order_items__quantity') * F('order_items__product_info__price_rrc')))
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer
    detail_serializer_class = OrderDetailSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.action == 'list':
            return queryset.filter(user=self.request.user).exclude(status='BASKET').prefetch_related(
                'order_items__product_info').all()
        elif self.action == 'retrieve':
            return queryset.filter(user=self.request.user).exclude(status='BASKET').prefetch_related(
                'order_items__product_info').all()

    def get_serializer_class(self):
        if self.action == 'retrieve':
            if hasattr(self, 'detail_serializer_class'):
                return self.detail_serializer_class
        return super(OrderViewSet, self).get_serializer_class()


class CreatingOrderView(APIView):
    """
        Создание нового заказа
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):

        if request.user.contact.type != 'BUYER':
            return Response({'status': 'Только для покупателей!'})

        try:
            order = Order.objects.get(user=request.user, status='BASKET')
        except Order.DoesNotExist:
            return Response({'status': 'У пользователя отсутствует товары в корзине'})

        order.status = 'NEW'
        order.save()
        return Response({'status': 'Заказ создан'})


class ConfirmOrderView(APIView):
    """
        Подтверждение заказа
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, order_id):

        if request.user.contact.type != 'BUYER':
            return Response({'status': 'Только для покупателей!'})

        try:
            order = Order.objects.get(id=order_id, user=request.user, status='NEW')
        except Order.DoesNotExist:
            return Response({'status': 'У пользователя отсутствуют новые неподтвержденные заказы'})

        order.status = 'CONFIRMED'
        order.save()
        send_email_order_confirm(order.user.id)
        return Response({'status': 'Заказ подтвержден'})
