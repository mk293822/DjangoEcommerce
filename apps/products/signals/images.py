from apps.core.services.file_services import FileServices
from apps.products.models.product import Product
from apps.products.models.variation_type import VariationTypeOptionImage 
from django.dispatch import receiver
from django.db.models.signals import pre_delete, pre_save, post_save

class ImageSignals:
    @staticmethod
    @receiver(pre_delete, sender=VariationTypeOptionImage)
    def delete_image_file(sender, instance, **kwargs):
        FileServices.delete_file_from_media(instance.image)
        
    @staticmethod
    @receiver(pre_save, sender=VariationTypeOptionImage)
    def remove_image_if_cleared(sender, instance, **kwargs):
        if not instance.pk:
            return
        
        try:
            old_option_image = VariationTypeOptionImage.objects.get(pk=instance.pk)
        except VariationTypeOptionImage.DoesNotExist:
            return
        
        if old_option_image.image and old_option_image.image != instance.image or not instance.image:
            FileServices.delete_file_from_media(old_option_image.image)
            
    @staticmethod
    @receiver(post_save, sender=VariationTypeOptionImage)
    def create_image_sizes_variation_type_option(sender, instance, **kwargs):
        if not instance.image:
            return
        
        sizes = {"large": (1024,1024), "medium": (512,512), "thumb": (128,128)}

        FileServices.resize_image(instance.image.path, sizes)
    
    @staticmethod
    @receiver(pre_delete, sender=Product)
    def delete_image_file_product(sender, instance, **kwargs):
        FileServices.delete_file_from_media(instance.image)
    
    @staticmethod
    @receiver(pre_save, sender=Product)
    def remove_image_if_cleared_product(sender, instance, **kwargs):
        if not instance.pk:
            return
        
        try:
            old_product = Product.objects.get(pk=instance.pk)
        except Product.DoesNotExist:
            return
        
        if old_product.image and old_product.image != instance.image or not instance.image:
            FileServices.delete_file_from_media(old_product.image)
    
    @staticmethod
    @receiver(post_save, sender=Product)
    def create_image_sizes_product(sender, instance, **kwargs):
        if not instance.image:
            return
        
        sizes = {"large": (1024,1024), "medium": (512,512), "thumb": (128,128)}
        FileServices.resize_image(instance.image.path, sizes)

    