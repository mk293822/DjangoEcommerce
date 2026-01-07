from django.db.models.signals import post_save
from django.dispatch import receiver
from guardian.shortcuts import assign_perm
from apps.products.models.product import Product, ProductVariation
from apps.products.models.variation_type import (
    VariationType,
    VariationTypeOption,
    VariationTypeOptionImage,
)

class ProductsPermissionServices:
    
    PERMS = ['view', 'change', 'delete']
    
    @staticmethod
    @receiver(post_save, sender=Product)
    def assign_product_permissions(sender, instance, created, **kwargs):
        if not created or not getattr(instance, "created_by"):
            return

        ProductsPermissionServices.assgn_parms(instance.created_by, instance, 'product')

        
    @staticmethod    
    @receiver(post_save, sender=ProductVariation)
    def assign_product_variation_permissions(sender, instance, created, **kwargs):
        if not created:
            return

        creator = instance.product.created_by
        if creator:
            ProductsPermissionServices.assgn_parms(creator, instance, 'productvariation')
            

    @staticmethod 
    @receiver(post_save, sender=VariationType)
    def assign_variation_type_permissions(sender, instance, created, **kwargs):
        if not created:
            return

        creator = instance.product.created_by
        if creator:
            ProductsPermissionServices.assgn_parms(creator, instance, 'variationtype')

    @staticmethod
    @receiver(post_save, sender=VariationTypeOption)
    def assign_variation_type_option_permissions(sender, instance, created, **kwargs):
        if not created:
            return

        creator = instance.variation_type.product.created_by
        if creator:
            ProductsPermissionServices.assgn_parms(creator, instance, 'variationtypeoption')

    @staticmethod
    @receiver(post_save, sender=VariationTypeOptionImage)
    def assign_variation_type_option_image_permissions(sender, instance, created, **kwargs):
        if not created:
            return

        creator = instance.variation_type_option.variation_type.product.created_by
        if creator:
            ProductsPermissionServices.assgn_parms(creator, instance, 'variationtypeoptionimage')
    
    @staticmethod
    def assgn_parms(user, instance, model_name):
        for perm in ProductsPermissionServices.PERMS:
            assign_perm(f"products.{perm}_{model_name}", user, instance)
