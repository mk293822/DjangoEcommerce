from django.db import models

class Status(models.TextChoices):
    DRAFT = 'draft', 'Draft'
    REQUIRES_PAYMENT = 'requires_payment', 'Requires Payment'
    PAID = 'paid', 'Paid'
    SHIPPED = 'shipped', 'Shipped'
    DELIVERED = 'delivered', 'Delivered'
    CANCELLED = 'cancelled', 'Cancelled'
    FAILED = 'failed', 'Failed'
