from django.urls import path
from . import views

urlpatterns = [
    path('', views.product_list, name='home'),
    path('cart/add', views.add_to_cart, name='add_to_cart')
]
