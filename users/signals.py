from django.apps import apps
from django.dispatch import receiver
from django.db.models.signals import post_migrate
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType


@receiver(post_migrate)
def create_roles_and_permissions(sender, **kwargs):
    if sender.name != 'users':
        return 

    print(f"Post-migrate signal received from app: {sender.name}")

    admin_group, _ = Group.objects.get_or_create(name='Admin')
    customer_group, _ = Group.objects.get_or_create(name='Customer')
    vendor_group, _ = Group.objects.get_or_create(name='Vendor')

    models = ['Department', 'Category', 'Product']

    for model_name in models:
        model = apps.get_model('products', model_name)
        content_type = ContentType.objects.get_for_model(model)

        admin_group.permissions.add(
            *Permission.objects.filter(content_type=content_type)
        )

        if model_name == 'Product':
            # Customer permissions
            customer_group.permissions.add(
                *Permission.objects.filter(
                    content_type=content_type,
                    codename__in=['view_product', 'buy_product']
                )
            )

            # Vendor permissions
            vendor_group.permissions.add(
                *Permission.objects.filter(
                    content_type=content_type,
                    codename__in=[
                        'add_product',
                        'change_product',
                        'view_product',
                        'delete_product',
                        'sold_product',
                        'buy_product',
                    ]
                )
            )
    print("Roles and permissions have been set up.")
