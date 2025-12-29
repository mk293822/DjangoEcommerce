from django.apps import apps
from django.dispatch import receiver
from django.db.models.signals import post_migrate
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType


@receiver(post_migrate)
def create_roles_and_permissions(sender, **kwargs):
    if sender.name != "users":
        return

    super_admin, _ = Group.objects.get_or_create(name="SuperAdmin")
    admin, _ = Group.objects.get_or_create(name="Admin")
    customer, _ = Group.objects.get_or_create(name="Customer")
    vendor, _ = Group.objects.get_or_create(name="Vendor")

    # SuperAdmin gets everything
    super_admin.permissions.set(Permission.objects.all())

    models = [
        "Department",
        "Category",
        "Product",
        "ProductVariation",
        "VariationType",
        "VariationTypeOption",
        "ProductVariationTypeOptionImage",
    ]

    for model_name in models:
        model = apps.get_model("products", model_name)
        content_type = ContentType.objects.get_for_model(model)

        perms = Permission.objects.filter(content_type=content_type)

        # Admin gets all perms for these models
        admin.permissions.add(*perms)

        if model_name == "Product":
            customer.permissions.add(
                *Permission.objects.filter(
                    content_type=content_type,
                    codename__in=["view_product", "buy_product"]
                )
            )

        if model_name not in ["Department", "Category"]:
            vendor.permissions.add(
                *Permission.objects.filter(
                    content_type=content_type,
                    codename__regex=r"^(add|change|delete|view|buy|sell)_"
                )
            )

    print("Roles and permissions created successfully")
