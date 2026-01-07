from django.db.models.signals import pre_delete
from apps.core.services.services import delete_file_from_media
from apps.products.models.variation_type import VariationTypeOption, VariationTypeOptionImage
from apps.products.services.product_variation import ProductVariationServices
from django.dispatch import receiver

@receiver(pre_delete, sender=VariationTypeOption)
def variation_type_option_pre_delete(sender, instance, **kwargs):
    ProductVariationServices.on_delete_option(instance)
    
@receiver(pre_delete, sender=VariationTypeOptionImage)
def delete_image_file(sender, instance, **kwargs):
    delete_file_from_media(instance.image)