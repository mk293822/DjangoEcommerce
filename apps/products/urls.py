from django.urls import path
from . import views

urlpatterns = [
    path('', views.product_list, name='home'),
    path('product/<slug:slug>/show', views.show_product, name='show_product'),
]
