from django.urls import path
from . import views

urlpatterns = [
    path('orders', views.orders, name='orders'),
    path('order_details/<str:order_id>', views.order_details, name='order_details'),
    path('checkout/', views.checkout_view, name='checkout_all'), 
    path('checkout/vendor/<int:vendor_id>/', views.checkout_view, name='checkout_vendor'),
]