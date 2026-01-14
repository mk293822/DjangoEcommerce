import os
from urllib.parse import urlencode

from apps.carts import models

class ProductServices:
    
    @staticmethod
    def get_product_context(products, cart):
        products_context = []
        for product in products:
            
            excluded_variation_ids = cart.items.filter(
                product=product,
                variation__isnull=False,
                variation__stock=models.F('quantity')
            ).values_list('variation_id', flat=True) if cart else []
            
            products_context.append({
                'product': product,
                'options_query': ProductServices.get_query_string(product=product, excluded_variation_ids=excluded_variation_ids),
            })
        return products_context
    
    @staticmethod
    def get_query_string(*, product, excluded_variation_ids = [], variation = None):
        selected_options = ProductServices.get_selected_options(product=product, variation=variation, excluded_variation_ids=excluded_variation_ids, return_ids=True, match_product_price=True)
        return urlencode(selected_options)
    
    @staticmethod
    def get_selected_options(
        *,
        selection_source = None, 
        product,
        variation = None,
        return_ids: bool = True,
        match_product_price: bool = True,
        excluded_variation_ids = None
    ):
        selected_options = {}
        
        variation_types = product.variation_types.all()
        product_variations = product.variations.all()
        if selection_source is None:
            selection_source = {}


        use_defaults = all(selection_source.get(vr_type.name) is None for vr_type in variation_types)
        if use_defaults and product_variations.exists():
            
            first_variation = variation
            if not first_variation:
                product_variations_qs  = product_variations
                if excluded_variation_ids is None:
                    excluded_variation_ids = []
                
                if match_product_price:
                    product_variations_qs  = product_variations.filter(price=product.price)
                    
                available_variations = product_variations_qs.exclude(id__in=excluded_variation_ids)
                
                if not available_variations.exists():
                    return {}

                first_variation = available_variations.first()
                    
            if first_variation:
                option_ids = first_variation.variation_type_option
                for vr_type, option_id in zip(variation_types, option_ids, strict=False):
                    selected_option = vr_type.options.filter(id=option_id).first()
                    if selected_option:
                        selected_options[vr_type.name] = selected_option

        else:
            for vr_type in variation_types:
                options_qs = vr_type.options.all()
                if not options_qs.exists():
                    continue

                req_id = selection_source.get(vr_type.name)
                selected_option = vr_type.options.filter(id=req_id).first() if req_id else options_qs.first()
                if selected_option:
                    selected_options[vr_type.name] = selected_option

        
        return ({k: v.id for k, v in selected_options.items()} if return_ids and selected_options else selected_options)

    
    @staticmethod
    def get_variation_type_option_images(variation_types):
 
        variation_type_option_images = {}
        for vr_type in variation_types:
            if not vr_type.options.exists():
                continue
            if vr_type.type == 'image':
                option_images = {}
                for option in vr_type.options.prefetch_related("images"):
                    if not option.images.exists():
                        continue
                    org_path = option.images.first().image.url
                    bs_path = os.path.dirname(org_path)
                    _, ext = os.path.splitext(org_path)
                    option_images[option.id] = {
                        "name": option.name,
                        "image": f"{bs_path}/thumb{ext}"
                    }
                variation_type_option_images[vr_type.name] = option_images

        return variation_type_option_images
    
    @staticmethod
    def get_carousel_images(has_variation, product, request):
        carousel_images = []
        selected_options: object = ProductServices.get_selected_options(selection_source=request.GET, product=product, return_ids=False, match_product_price=False)
        if has_variation and selected_options:

            for _, sel_option in selected_options.items():
                if sel_option.variation_type.type != 'image' or not sel_option.images.exists():
                    continue
                for img in sel_option.images.all():
                    org_path_sel = img.image.url
                    b_path = os.path.dirname(org_path_sel)
                    _, ext = os.path.splitext(org_path_sel)
                    carousel_images.append({
                        'large': f"{b_path}/large{ext}",
                        'thumb': f"{b_path}/thumb{ext}",
                    })
        else:
            org_path_product = product.image.url
            base_path = os.path.dirname(org_path_product)
            _, ext = os.path.splitext(org_path_product)
            carousel_images.append({
                'large': f"{base_path}/large{ext}",
                'thumb': f"{base_path}/thumb{ext}",
            })
    
        
        return carousel_images