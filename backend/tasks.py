from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.contrib.auth.models import User


def send_email_registration(user_id: int, **kwargs):
    """
    Отправка письма на почту при регистрации пользователя
    """

    user = User.objects.get(id=user_id)
    subject = 'Подтверждение регистрации'
    to = [user.email,]
    body = f'Регистрация прошла успешно. Ваш логин: {user.username}'
    message = EmailMultiAlternatives(subject=subject, body=body, from_email=settings.EMAIL_HOST_USER, to=to)
    message.send()


def send_email_order_confirm(user_id: int, **kwargs):
    """
        Отправка письма на почту при подтверждении заказа
    """

    user = User.objects.get(id=user_id)
    subject = 'Подтверждение заказа'
    to = [user.email,]
    body = f'Ваш заказ успешно подтвержден'
    message = EmailMultiAlternatives(subject=subject, body=body, from_email=settings.EMAIL_HOST_USER, to=to)
    message.send()
