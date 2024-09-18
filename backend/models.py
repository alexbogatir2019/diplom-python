from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum


class OrderStatusChoices(models.TextChoices):
    """
        Статусы заказа
    """
    BASKET = 'OPEN', 'Статус корзины'
    NEW = 'NEW', 'Новый'
    CONFIRMED = 'CONFIRMED', 'Подтвержден'
    ASSEMBLED = 'ASSEMBLED', 'Собран'
    SENT = 'SENT', 'Отправлен'
    DELIVERED = 'DELIVERED', 'Доставлен'
    CANCELED = 'CANCELED', 'Отменен'


class UserTypeChoices(models.TextChoices):
    """
        Типы пользователей
    """
    SHOP = 'SHOP', 'Магазин'
    BUYER = 'BUYER', 'Покупатель'


class Contact(models.Model):
    """
        Модель контакта
    """
    user = models.OneToOneField(User, related_name='contact', on_delete=models.CASCADE)
    type = models.TextField(choices=UserTypeChoices.choices, default=UserTypeChoices.BUYER)
    phone = models.CharField(max_length=20, verbose_name='Номер телефона', blank=True, null=True)
    city = models.CharField(max_length=100, verbose_name='Город', blank=True, null=True)
    street = models.CharField(max_length=100, verbose_name='Улица', blank=True, null=True)
    house = models.CharField(max_length=100, verbose_name='Дом', blank=True, null=True)
    structure = models.CharField(max_length=100, verbose_name='Корпус', blank=True, null=True)
    building = models.CharField(max_length=100, verbose_name='Строение', blank=True, null=True)
    apartment = models.CharField(max_length=100, verbose_name='Квартира', blank=True, null=True)

    def __str__(self):
        return f'{self.user} - {self.type}'


class Shop(models.Model):
    """
        Модель магазина
    """
    name = models.CharField(max_length=100, verbose_name='Название магазина')
    url = models.URLField(verbose_name='Ссылка', null=True, blank=True)
    owner = models.OneToOneField(Contact, related_name='shop', verbose_name='Владелец', on_delete=models.CASCADE)
    state = models.BooleanField(verbose_name='Статус', default=True)

    def __str__(self):
        return self.name


class Category(models.Model):
    """
        Модель Категории товара
    """
    name = models.CharField(max_length=100, verbose_name='Название категории')
    shops = models.ManyToManyField(Shop, related_name='categories', verbose_name='Магазины')

    def __str__(self):
        return self.name


class Product(models.Model):
    """
        Модель товара
    """
    name = models.CharField(max_length=100, verbose_name='Название')
    category = models.ForeignKey(Category, related_name='products', verbose_name='Категория', on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class ProductInfo(models.Model):
    """
        Модель информации о продукте
    """
    product = models.ForeignKey(Product, related_name='product_info', verbose_name='Продукт', on_delete=models.CASCADE)
    shop = models.ForeignKey(Shop, related_name='product_info', verbose_name='Магазин', on_delete=models.CASCADE)
    model = models.CharField(max_length=100, verbose_name='Модель', blank=True)
    quantity = models.PositiveIntegerField(verbose_name='Количество', default=1)
    price = models.PositiveIntegerField(verbose_name='Цена')
    price_rrc = models.PositiveIntegerField(verbose_name='Рекомендуемая розничная цена')


class Parameter(models.Model):
    """
        Модель параметра
    """
    name = models.CharField(max_length=100, verbose_name='Название параметра')

    def __str__(self):
        return self.name


class ProductParameter(models.Model):
    """
        Модель параметров продукта
    """
    product_info = models.ForeignKey(ProductInfo, related_name='product_parameters',
                                     verbose_name='Информация о продукте', blank=True, on_delete=models.CASCADE)
    parameter = models.ForeignKey(Parameter, related_name='product_parameters',
                                  verbose_name='Параметр', on_delete=models.CASCADE)
    value = models.CharField(max_length=100, verbose_name='Значение')


class Order(models.Model):
    """
        Модель заказа
    """
    user = models.ForeignKey(User, related_name='orders', verbose_name='Пользователь', on_delete=models.CASCADE)
    dt = models.DateTimeField(auto_now_add=True)
    status = models.TextField(choices=OrderStatusChoices.choices, verbose_name='Статус',
                              default=OrderStatusChoices.BASKET)

    def __str__(self):
        return str(f'Заказ No{self.pk} от {self.dt} для {self.user}')


class OrderItem(models.Model):
    """
        Модель элемента заказа
    """
    order = models.ForeignKey(Order, related_name='order_items', on_delete=models.CASCADE)
    product_info = models.ForeignKey(ProductInfo, related_name='order_items', on_delete=models.CASCADE, null=True)
    shop = models.ForeignKey(Shop, related_name='order_items', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
