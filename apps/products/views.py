from django.shortcuts import render
from apps.carts.models import Cart
from apps.carts.services import CartServices
from apps.departments.models import Department
from apps.products.models.variation_type import VariationType
from apps.products.services.product_details import ProductServices
from .models.product import Product, ProductVariation
import json
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models

# Create your views here.
def product_list(request):
    
    query = request.GET.get('q', '')
    department_id = request.GET.get('department', 'all')
    products = Product.objects.active()
    departments = Department.objects.filter(status=True)
    cart, _ = Cart.objects.get_or_create(user=request.user) if request.user.is_authenticated else None
    
    if department_id != "all":
        products = products.filter(department_id=department_id)
        
    products = products.search(query)
    
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
    
    context = {
        'products_context': products_context, 
        'departments': departments, 
        'selected_department': department_id, 
        'query': query,
    } 
    context.update(CartServices.get_cart_context(request.user))        

    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return render(request, "products/components/products_list.html", {"products": products})
    
    return render(request, 'products/home.html', context)

def product_details(request, slug):
    
    product: Product = Product.objects.get(slug=slug)
    product_variations: ProductVariation = product.variations.all()
    has_variation: bool = product_variations.count() > 0
    variation_types: VariationType = VariationType.objects.filter(product=product)
    carousel_images = ProductServices.get_carousel_images(has_variation, product, request)
    context = {
        'product': product,
        'has_variation': has_variation,
        'carousel_images': carousel_images,
        'created_by': product.created_by.name,
        'quantity': range(1, product.max_quantity + 1)
    }
    
    context.update(CartServices.get_cart_context(request.user))        
    
    pr_variations = {}
    for variation in product_variations:
        pr_variations[variation.id] = {
            'stock': variation.stock,
            'price': float(variation.price),
            'variation_type_options': variation.variation_type_option
        }
    
    if has_variation:
        context.update({
            'variation_types': variation_types,
            'product_variations': json.dumps(pr_variations, cls=DjangoJSONEncoder),
            'selected_options': json.dumps(ProductServices.get_selected_options(selection_source=request.GET, product=product, return_ids=True, match_product_price=False), cls=DjangoJSONEncoder),
            'variation_type_option_images': ProductServices.get_variation_type_option_images(variation_types),
        })
    
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return render(request, "products/components/carousel.html", {"product": product, "carousel_images": carousel_images})
    
    return render(request, 'products/product_details.html', context)

 
    