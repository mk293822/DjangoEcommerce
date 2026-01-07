    
import uuid
from django.db import models
import os
from .product import Product
from django.db import transaction

def image_upload_to(instance, filename):
    type_instance = instance.variation_type_option.variation_type
    ext = filename.split('.')[-1]
        
    return os.path.join(f"product_images/{type_instance.product.id}/variations/type{type_instance.id}/option{instance.variation_type_option.id}/", str(uuid.uuid4())[:8],f"original.{ext}")
    


class VariationType(models.Model):
    """Defines a type of variation for a Product (e.g., Size, Color).

    The `type` field can be used to indicate input or presentation details.
    """
    
    types  = [
        ('select', 'Select'),
        ('radio', 'Radio'),
        ('image', 'Image'),
    ]
    
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=100, choices=types, default='select')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variation_types')

    def __str__(self):
        return self.name


class VariationTypeOption(models.Model):
    """An option/value for a VariationType (e.g., 'Red' for Color, 'XL' for Size).

    Options are tied to a VariationType and used by ProductVariation.
    """
    
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    variation_type = models.ForeignKey(VariationType, on_delete=models.CASCADE, null=True, related_name='options')

    def __str__(self):
        return self.name
    

class VariationTypeOptionImage(models.Model):
    """An image belonging to a Product Variation Type Options, with optional alt text and display order.

    Images are uploaded to 'product_images/' and can be ordered for presentation.
    """
    id = models.AutoField(primary_key=True)
    variation_type_option = models.ForeignKey(VariationTypeOption, on_delete=models.CASCADE, related_name='images', max_length=500)
    image = models.ImageField(upload_to=image_upload_to)
    alt_text = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    order = models.PositiveIntegerField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.variation_type_option} - Image {self.order}"

    def save(self, *args, **kwargs):
        with transaction.atomic():
            last_order = (
                VariationTypeOptionImage.objects
                .filter(variation_type_option=self.variation_type_option)
                .aggregate(models.Max("order"))["order__max"]
            )

            existing_orders = set(
                VariationTypeOptionImage.objects
                .filter(variation_type_option=self.variation_type_option)
                .values_list("order", flat=True)
            )

            if not self.order or self.order in existing_orders:
                self.order = (last_order or 0) + 1

        super().save(*args, **kwargs)


    class Meta:
        ordering = ['order']
        constraints = [
            models.UniqueConstraint(fields=['variation_type_option', 'order'], name='unique_variation_option_image_order')
        ]
        
    