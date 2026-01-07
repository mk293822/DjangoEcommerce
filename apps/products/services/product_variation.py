from itertools import product as iterator_product
from apps.products.models.variation_type import VariationType
from apps.products.models.product import Product, ProductVariation
from django.db import transaction


class ProductVariationServices:
    
    @staticmethod
    def on_delete(variation):
        variations = variation.product.variations.exclude(id=variation.id)
        product_stock = variation.product.stock
        base_qty = product_stock // variations.count()
        remainder = product_stock % variations.count()
        
        if variations.count() == 0:
            return
        
        for i, vr in enumerate(variations):
            vr.stock = base_qty + (1 if i < remainder else 0)
            vr.save(update_fields=['stock'])
        
        

    @staticmethod 
    def on_create_option(product_id):
        product = Product.objects.select_for_update().get(id=product_id)
        variation_types = VariationType.objects.filter(product=product)

        options_matrix = []

        for variation_type in variation_types:
            opts = list(variation_type.options.values_list("id", flat=True))
            if not opts:
                return
            options_matrix.append(opts)

        combinations = list(iterator_product(*options_matrix))
        if not combinations:
            return

        total_stock = product.stock
        base_qty = total_stock // len(combinations)
        remainder = total_stock % len(combinations)

        with transaction.atomic():
            ProductVariation.objects.filter(product=product).delete()

            for i, combo in enumerate(combinations):
                ProductVariation.objects.create(
                    product=product,
                    variation_type_option=sorted(combo),
                    stock=base_qty + (1 if i < remainder else 0),
                    price=product.price,
                )

    @staticmethod            
    def on_delete_option(option):
        product = option.variation_type.product
        variations = ProductVariation.objects.filter(product=product)
        
        with transaction.atomic():
            for variation in variations:
                opts = variation.variation_type_option or []
                if option.id not in opts:
                    continue

                new_opts = [opt_id for opt_id in opts if opt_id != option.id]

                duplicate_exists = any(
                    all(opt in v.variation_type_option for opt in new_opts)
                    for v in variations
                    if v.id != variation.id
                )

                if duplicate_exists or not new_opts:
                    variation.delete()
                else:
                    variation.variation_type_option = new_opts
                    variation.save(update_fields=["variation_type_option"])
                    
            remaining_variations = ProductVariation.objects.filter(product=product)
            
            if remaining_variations.count() == variations.count():
                return
            
            total_stock = product.stock
            n = remaining_variations.count()
            if n == 0:
                return
            base_qty = total_stock // n
            remainder = total_stock % n
            for idx, var in enumerate(remaining_variations):
                var.stock = base_qty + (1 if idx < remainder else 0)
                var.save(update_fields=["stock"])