from django.urls import path
from . import views

urlpatterns = [
    path('', views.product_list, name='home'),
    path('product/<slug:slug>/details', views.product_details, name='product_details'),
]
