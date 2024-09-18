"""
URL configuration for orders project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.routers import DefaultRouter

from backend.views import ShopViewSet, CategoryViewSet, UserRegistrationView, LoginView, \
    ContactView, LogoutView, BasketView, ProductViewSet, SupplierUpdate, ParameterViewSet, OrderViewSet, \
    CreatingOrderView, ConfirmOrderView

r = DefaultRouter()
r.register('shops', ShopViewSet)
r.register('categories', CategoryViewSet)
r.register('products', ProductViewSet)
r.register('orders', OrderViewSet)
r.register('parameters', ParameterViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('registration/', UserRegistrationView.as_view(), name='registration_user'),
    path('token/', obtain_auth_token),
    path('login/', LoginView.as_view(), name='login_user'),
    path('logout/', LogoutView.as_view(), name='logout_user'),
    path('contact/', ContactView.as_view(), name='contact'),
    path('basket/', BasketView.as_view(), name='basket'),
    path('new_order/', CreatingOrderView.as_view(), name='new_order'),
    path('confirm_order/<int:order_id>/', ConfirmOrderView.as_view(), name='confirm_order'),
    path('update/<str:file_name>/', SupplierUpdate.as_view(), name='update'),
] + r.urls
