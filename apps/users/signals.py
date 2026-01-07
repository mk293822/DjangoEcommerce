from django.apps import apps
from django.dispatch import receiver
from django.db.models.signals import post_migrate, pre_delete, pre_save
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from apps.users.models import User
from .constants import *
from django.db import transaction
from apps.core.services import delete_file_from_media

@receiver(post_migrate)
def create_roles_and_permissions(sender, **kwargs):
    with transaction.actomic():
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

@receiver(pre_delete, sender=User)
def delete_avatar_on_user_delete(sender, instance, **kwargs):
    delete_file_from_media(instance.avatar)

@receiver(pre_save, sender=User)
def remove_avatar_if_cleared(sender, instance: User, **kwargs):
    if not instance.pk:
        return
    
    try:
        old_user = User.objects.get(pk=instance.pk)
    except User.DoesNotExist:
        return
    
    if old_user.avatar and not instance.avatar:
        delete_file_from_media(old_user.avatar)