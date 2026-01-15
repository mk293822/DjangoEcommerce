from django.apps import apps
from django.dispatch import receiver
from django.db.models.signals import post_migrate, pre_delete, pre_save, post_save
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from apps.users.models import User, Vendor
from .constants import *
from django.db import transaction
from apps.core.services.file_services import FileServices

IMAGE_SIZES = {
    "large": (1024, 1024),
    "thumb": (128, 128),
}

@receiver(pre_delete, sender=User)
def delete_avatar_on_user_delete(sender, instance, **kwargs):
    FileServices.delete_file_from_media(instance.avatar)

@receiver(pre_save, sender=User)
def remove_avatar_if_cleared(sender, instance: User, **kwargs):
    if not instance.pk:
        return
    
    old_user = User.objects.get(pk=instance.pk)
    
    if old_user.avatar and not instance.avatar:
        FileServices.delete_file_from_media(old_user.avatar)

@receiver(post_save, sender=User)
def resize_user_avatar(sender, instance, **kwargs):
    if instance.avatar:
        FileServices.resize_image(instance.avatar.path, IMAGE_SIZES)
    
# Vendor
@receiver(pre_delete, sender=Vendor)
def delete_cover_image_on_vendor_delete(sender, instance, **kwargs):
    FileServices.delete_file_from_media(instance.cover_image)

@receiver(pre_save, sender=Vendor)
def remove_cover_image_if_cleared(sender, instance: Vendor, **kwargs):
    if not instance.pk:
        return
    
    old_vendor = Vendor.objects.get(pk=instance.pk)
    
    if old_vendor.cover_image and not instance.cover_image:
        FileServices.delete_file_from_media(old_vendor.cover_image)

@receiver(post_save, sender=Vendor)
def resize_vendor_cover_image(sender, instance, **kwargs):
    if instance.cover_image:
        FileServices.resize_image(instance.cover_image.path, IMAGE_SIZES)
        

# Migrate roles and permissions
@receiver(post_migrate)
def create_roles_and_permissions(sender, **kwargs):
    with transaction.atomic():
        if sender.label != "users":
            return

        admin, _ = Group.objects.get_or_create(name=GROUP_ADMIN)
        customer, _ = Group.objects.get_or_create(name=GROUP_CUSTOMER)
        vendor, _ = Group.objects.get_or_create(name=GROUP_VENDOR)

        products_models = [
            "Product",
            "ProductVariation",
            "VariationType",
            "VariationTypeOption",
            "VariationTypeOptionImage",
        ]
        
        department_models = [
            "Department",
            "Category",
        ]

        for model_name in products_models:
            model = apps.get_model("products", model_name)
            content_type = ContentType.objects.get_for_model(model)
            perms = Permission.objects.filter(content_type=content_type)
            # Admin gets all perms for these models
            admin.permissions.add(*perms)
            
        for model_name in department_models:
            model = apps.get_model("departments", model_name)
            content_type = ContentType.objects.get_for_model(model)
            perms = Permission.objects.filter(content_type=content_type)
            # Admin gets all perms for these models
            admin.permissions.add(*perms)
        
        product_model = apps.get_model("products", "Product")
        product_ct = ContentType.objects.get_for_model(product_model)

        # ✅ SAFE permission creation
        view_product_perm, _ = Permission.objects.get_or_create(
            codename="view_product",
            content_type=product_ct,
            defaults={"name": "Can view product"},
        )

        customer.permissions.add(view_product_perm)
        
        vendor.permissions.add(
                *Permission.objects.filter(
                    codename__in=[
                    'sell_product',
                    'add_product',
                    'view_product',
                    'view_department',
                    'view_category',
                    'add_variationtype',
                    'add_variationtypeoption',
                    'add_variationtypeoptionimage',
                    'view_variationtype',
                    'view_variationtypeoption',
                    'view_variationtypeoptionimage',
                    'view_productvariation'
                    ]
                )
            )

                

        print("Roles and permissions created successfully")
