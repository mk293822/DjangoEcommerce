from django.db.models.signals import post_save
from django.dispatch import receiver
from guardian.shortcuts import assign_perm
from apps.products.models.product import Product, ProductVariation
from apps.products.models.variation_type import (
    VariationType,
    VariationTypeOption,
    VariationTypeOptionImage,
)


@receiver(post_save, sender=Product)
def assign_product_permissions(sender, instance, created, **kwargs):
    if not created or not getattr(instance, "created_by"):
        return

    assign_perm("products.change_product", instance.created_by, instance)
    assign_perm("products.delete_product", instance.created_by, instance)
    assign_perm("products.view_product", instance.created_by, instance)
    
    
@receiver(post_save, sender=ProductVariation)
def assign_product_variation_permissions(sender, instance, created, **kwargs):
    if not created:
        return

    creator = instance.product.created_by
    if creator:
        assign_perm("products.change_productvariation", creator, instance)
        assign_perm("products.delete_productvariation", creator, instance)
        assign_perm("products.view_productvariation", creator, instance)
        
    


@receiver(post_save, sender=VariationType)
def assign_variation_type_permissions(sender, instance, created, **kwargs):
    if not created:
        return

    creator = instance.product.created_by
    if creator:
        assign_perm("products.change_variationtype", creator, instance)
        assign_perm("products.delete_variationtype", creator, instance)
        assign_perm("products.view_variationtype", creator, instance)

    


@receiver(post_save, sender=VariationTypeOption)
def assign_variation_type_option_permissions(sender, instance, created, **kwargs):
    if not created:
        return

    creator = instance.variation_type.product.created_by
    if creator:
        assign_perm("products.change_variationtypeoption", creator, instance)
        assign_perm("products.delete_variationtypeoption", creator, instance)
        assign_perm("products.view_variationtypeoption", creator, instance)

    


@receiver(post_save, sender=VariationTypeOptionImage)
def assign_variation_type_option_image_permissions(sender, instance, created, **kwargs):
    if not created:
        return

    creator = instance.variation_type_option.variation_type.product.created_by
    if creator:
        assign_perm(
            "products.change_variationtypeoptionimage", creator, instance
        )
        assign_perm(
            "products.delete_variationtypeoptionimage", creator, instance
        )
        assign_perm(
            "products.view_variationtypeoptionimage", creator, instance
        )

    
