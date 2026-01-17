from django.urls import path
from . import views

urlpatterns = [
    path('stripe/checkout', views.checkout, name='stripe_checkout'),
    path('stripe/success', views.stripe_success, name='stripe_success'),
    path('stripe/failure', views.stripe_failure, name='stripe_failure'),
]
