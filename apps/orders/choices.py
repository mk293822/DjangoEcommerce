
from django.db import models

class Status(models.TextChoices):
    DRAFT = 'draft', 'Draft'
    PAID = 'paid', 'Paid'
    SHIPPED = 'shipped', 'Shipped'
    DELIVERED = 'delivered', 'Delivered'
    CANCELLED = 'cancelled', 'Cancelled'
