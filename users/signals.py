from django.apps import apps
from django.dispatch import receiver
from django.db.models.signals import post_migrate
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from .constants import *

@receiver(post_migrate)
def create_roles_and_permissions(sender, **kwargs):
    if sender.name != "users":
        return

    admin, _ = Group.objects.get_or_create(name=GROUP_ADMIN)
    customer, _ = Group.objects.get_or_create(name=GROUP_CUSTOMER)
    vendor, _ = Group.objects.get_or_create(name=GROUP_VENDOR)

    models = [
        "Department",
        "Category",
        "Product",
        "ProductVariation",
        "VariationType",
        "VariationTypeOption",
        "VariationTypeOptionImage",
    ]

    for model_name in models:
        model = apps.get_model("products", model_name)
        content_type = ContentType.objects.get_for_model(model)
        perms = Permission.objects.filter(content_type=content_type)
        # Admin gets all perms for these models
        admin.permissions.add(*perms)
        
    customer.permissions.add(Permission.objects.get(codename='view_product'))
    
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
                   'view_vairiationtypeoption',
                   'view_variationtypeoptionimage',
                   'view_productvariation'
                ]
            )
        )

            

    print("Roles and permissions created successfully")
