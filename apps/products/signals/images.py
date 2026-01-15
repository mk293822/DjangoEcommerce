from django.db.models.signals import pre_delete, pre_save, post_save
from django.dispatch import receiver
from apps.core.services.file_services import FileServices
from apps.products.models.product import Product
from apps.products.models.variation_type import VariationTypeOptionImage

IMAGE_SIZES = {
    "large": (1024, 1024),
    "medium": (512, 512),
    "thumb": (128, 128),
}

def delete_old_image(old_image, new_image):
    if old_image and (old_image != new_image or not new_image):
        FileServices.delete_file_from_media(old_image)


@receiver(pre_delete, sender=VariationTypeOptionImage)
def delete_variation_image(sender, instance, **kwargs):
    FileServices.delete_file_from_media(instance.image)


@receiver(pre_save, sender=VariationTypeOptionImage)
def replace_variation_image(sender, instance, **kwargs):
    if not instance.pk:
        return

    old = VariationTypeOptionImage.objects.filter(pk=instance.pk).first()
    if old:
        delete_old_image(old.image, instance.image)


@receiver(post_save, sender=VariationTypeOptionImage)
def resize_variation_image(sender, instance, **kwargs):
    if instance.image:
        FileServices.resize_image(instance.image.path, IMAGE_SIZES)


@receiver(pre_delete, sender=Product)
def delete_product_image(sender, instance, **kwargs):
    FileServices.delete_file_from_media(instance.image)


@receiver(pre_save, sender=Product)
def replace_product_image(sender, instance, **kwargs):
    if not instance.pk:
        return

    old = Product.objects.filter(pk=instance.pk).first()
    if old:
        delete_old_image(old.image, instance.image)


@receiver(post_save, sender=Product)
def resize_product_image(sender, instance, **kwargs):
    if instance.image:
        FileServices.resize_image(instance.image.path, IMAGE_SIZES)
