from django.dispatch import receiver
from django.db.models.signals import post_save, pre_delete
from apps.products.models.variation_type import VariationType, VariationTypeOption
from apps.products.models.product import ProductVariation
from itertools import product as iterator_product

@receiver(post_save, sender=VariationType)
def create_variation_type_options(sender, instance, created, **kwargs):
    if created:
        ProductVariation.objects.filter(product=instance.product).delete()

@receiver(post_save, sender=VariationTypeOption)
def create_product_variation(sender, instance, created, **kwargs):
    if created:
        product = instance.variation_type.product
        variation_types = VariationType.objects.filter(product=product)
        
        options_dict = []
        for variation_type in variation_types:
            options = list(variation_type.options.values_list('id', flat=True))
            if options:
                # append only if there are options available
                options_dict.append(options)
        
        option_combinations = list(iterator_product(*options_dict))
        combinations_len = len(option_combinations)
        total_stock = product.stock
        base_qty = total_stock // combinations_len
        remainder = total_stock % combinations_len
        
        for index, combination in enumerate(option_combinations):
            stock = base_qty + (1 if index < remainder else 0)
            combination_sort = sorted(list(combination))
            
            exist = ProductVariation.objects.filter(
                product=product,
                variation_type_option=combination_sort
            ).exists()
            
            if not exist:
                ProductVariation.objects.create(
                    product=product,
                    variation_type_option=combination_sort,
                    stock=stock,
                    price=product.price
                )

@receiver(pre_delete, sender=VariationType)
def delete_variation_type(sender, instance, **kwargs):
    options = instance.options.all()
    
    for op in options:
        op.delete()
        
@receiver(pre_delete, sender=VariationTypeOption)
def delete_variation_type_option(sender, instance, **kwargs):
    product = instance.variation_type.product
    variations = ProductVariation.objects.filter(product=product)
    variation_type_option_count = instance.variation_type.options.count()

    for variation in variations:
        opts = variation.variation_type_option or []
        if instance.id in opts:
            if variation_type_option_count > 1:
                variation.delete()
            else:
                variation.variation_type_option = [
                    opt_id for opt_id in opts if opt_id != instance.id
                ]
                variation.save(update_fields=["variation_type_option"])
                