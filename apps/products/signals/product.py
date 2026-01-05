from django.db.models.signals import pre_save
from django.dispatch import receiver
from apps.products.models.product import Product
from apps.products.services.slug_service import SlugService

@receiver(pre_save, sender=Product)
def set_product_slug(sender, instance, **kwargs):
    SlugService.assign_slug_to_model(instance)
    