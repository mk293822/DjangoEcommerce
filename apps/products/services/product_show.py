import os
from apps.products.models.variation_type import VariationTypeOption


class ProductServices:
    
    @staticmethod
    def get_selected_options(request, variation_types, product_variation=None, context=True):

        selected_options = {}

        use_variation_defaults = all(request.GET.get(vr_type.name) is None for vr_type in variation_types)

        if use_variation_defaults and product_variation:
            first_variation = product_variation.first()
            option_ids = first_variation.variation_type_option

            for vr_type, option_id in zip(variation_types, option_ids):
                if not vr_type.options.exists():
                    continue
                selected_option = vr_type.options.get(id=option_id)
                selected_options[vr_type.name] = selected_option
        else:
            for vr_type in variation_types:
                if not vr_type.options.exists():
                    continue

                req_id = request.GET.get(vr_type.name)
                if req_id and vr_type.options.filter(id=req_id).exists():
                    selected_option = vr_type.options.get(id=req_id)
                else:
                    selected_option = vr_type.options.first()

                selected_options[vr_type.name] = selected_option

        if not context:
            return selected_options

        return {t: v.id for t, v in selected_options.items()}

    
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
    def get_carousel_images(has_variation, product, request, variation_types):
        carousel_images = []
        selected_options: object = ProductServices.get_selected_options(request, variation_types, None, False)
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