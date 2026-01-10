from django.db.models.signals import pre_delete
from apps.products.services.product_variation import ProductVariationServices
from apps.products.models.variation_type import VariationTypeOption
from django.dispatch import receiver

@receiver(pre_delete, sender=VariationTypeOption)
def variation_type_option_pre_delete(sender, instance, **kwargs):
    ProductVariationServices.on_delete_option(instance)