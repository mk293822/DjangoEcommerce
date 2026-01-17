# File: apps/orders/models/order.py

import uuid
from django.db import models
from django.conf import settings
from .choices import Status
from apps.products.models.product import Product, ProductVariation


class Order(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='orders'
    )

    vendor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='vendor_orders',
        null=True,
        blank=True
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

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

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

    variation = models.ForeignKey(
        ProductVariation,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} (Order {self.order.id})"
