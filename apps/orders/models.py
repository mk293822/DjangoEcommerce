from re import S
import uuid
from django.db import models
from django.conf import settings
from .choices import Status
from apps.products.models.product import Product

class Order(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    vendor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name='vendor_orders', null=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0) 
    stripe_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)  
    platform_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)  
    vendor_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    paid = models.BooleanField(default=False)
    stripe_checkout_session_id = models.CharField(max_length=255, blank=True, null=True)
    stripe_payment_intent_id = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def calculate_fees(self):
        self.vendor_amount = self.total_amount - self.stripe_fee - self.platform_fee
        return self.vendor_amount

    def __str__(self):
        return f"Order {self.id} - {self.user}"

class OrderItem(models.Model):
    id = models.AutoField(primary_key=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='order_items')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    variation_type_option_ids = models.JSONField(blank=True, null=True)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in Order {self.order.id}"