from django.db import transaction
from products.models import ProductVariation

def delete_option(option):

    variation_type = option.variation_type
    product = variation_type.product
    total_options = variation_type.options.count()

    variations = ProductVariation.objects.filter(product=product)

    with transaction.atomic():
        for variation in variations:
            opts = variation.variation_type_option or []

            if option.id not in opts:
                continue

            if total_options > 1:
                variation.delete()
            else:
                variation.variation_type_option = [
                    opt_id for opt_id in opts if opt_id != option.id
                ]
                variation.save(update_fields=["variation_type_option"])

        option.delete()
