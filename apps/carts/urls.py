from django.urls import path
from . import views

urlpatterns = [
    path('', views.carts, name='carts'),
    path('add', views.add_to_cart, name='add_to_cart'),
]
