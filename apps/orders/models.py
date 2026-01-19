# File: apps/orders/models/order.py

import uuid
from django.db import models
from django.conf import settings

from apps.core.services.file_services import FileServices
from .choices import Status
from apps.products.models.product import Product, ProductVariation


class Order(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='orders'
    )

    vendor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='vendor_orders',
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT
    )

    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    platform_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    vendor_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    stripe_checkout_session_id = models.CharField(
        max_length=255, blank=True, null=True, db_index=True
    )

    stripe_payment_intent_id = models.CharField(
        max_length=255, blank=True, null=True, db_index=True
    )
    
    shipping_name = models.CharField(max_length=255, blank=True)
    shipping_address = models.TextField(blank=True)
    shipping_city = models.CharField(max_length=100, blank=True)
    shipping_state = models.CharField(max_length=100, blank=True)
    shipping_zip = models.CharField(max_length=20, blank=True)
    shipping_country = models.CharField(max_length=100, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def recalculate_totals(self, save=False):
        total = sum(
            item.price * item.quantity
            for item in self.items.all()
        )
        self.total_amount = total
        self.calculate_vendor_amount()
        if save:
            self.save(update_fields=['total_amount', 'vendor_amount'])
        return self.total_amount


    def calculate_vendor_amount(self, save=False):
        self.vendor_amount = (
            self.total_amount - self.platform_fee
        )
        if save:
            self.save(update_fields=['vendor_amount'])
        return self.vendor_amount

    def __str__(self):
        return f"Order {self.id} - {self.user}"


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items'
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='order_items'
    )

    variation = models.ForeignKey(ProductVariation, on_delete=models.SET_NULL, null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    
    class Meta:
        unique_together = ('order', 'product', 'variation')

    def image(self):
        return FileServices.get_image(self.product, self.variation)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} (Order {self.order.id})"
