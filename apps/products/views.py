from django.shortcuts import render
from apps.departments.models import Department
from apps.products.models.variation_type import VariationType
from apps.products.services.product_show import ProductServices
from .models.product import Product, ProductVariation
from apps.carts.models import Cart, CartItem
import json
from django.core.serializers.json import DjangoJSONEncoder

# Create your views here.
def product_list(request):
    
    query = request.GET.get('q', '')
    department_id = request.GET.get('department', 'all')
    products = Product.objects.active()
    departments = Department.objects.filter(status=True)
    
    if department_id != "all":
        products = products.filter(department_id=department_id)
        
    products = products.search(query)
    
    products_context = []
    for product in products:
        variation_types: VariationType = VariationType.objects.filter(product=product)
        product_variations = ProductVariation.objects.filter(product=product)
        selected_options = ProductServices.get_selected_options(request, variation_types, product_variations)
        query_string = "&".join(f"{k}={v}" for k, v in selected_options.items())
        products_context.append({
            'product': product,
            'options_query': query_string,
        })
    
    context = {
        'products_context': products_context, 
        'departments': departments, 
        'selected_department': department_id, 
        'query': query,
    } 
    
    if request.user.is_authenticated:    
        cart, _ = Cart.objects.get_or_create(user=request.user)
        cart_items = CartItem.objects.filter(cart=cart)
        
        context.update({
            'cart': cart , 
            'cart_items': cart_items,
        })        

    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return render(request, "products/components/products_list.html", {"products": products})
    
    return render(request, 'products/home.html', context)

def show_product(request, slug):
    
    product: Product = Product.objects.get(slug=slug)
    product_variations: ProductVariation = product.variations.all()
    has_variation: bool = product_variations.count() > 0
    variation_types: VariationType = VariationType.objects.filter(product=product)
    carousel_images = ProductServices.get_carousel_images(has_variation, product, request, variation_types)
    
    context = {
        'product': product,
        'has_variation': has_variation,
        'carousel_images': carousel_images,
        'created_by': product.created_by.name
    }
    
    if request.user.is_authenticated:    
        cart, _ = Cart.objects.get_or_create(user=request.user)
        cart_items = CartItem.objects.filter(cart=cart)
        
        context.update({
            'cart': cart , 
            'cart_items': cart_items,
        })
    
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
            'selected_options': json.dumps(ProductServices.get_selected_options(request, variation_types, product_variations), cls=DjangoJSONEncoder),
            'variation_type_option_images': ProductServices.get_variation_type_option_images(variation_types),
        })
    
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return render(request, "products/components/carousel.html", {"product": product, "carousel_images": carousel_images})
    
    return render(request, 'products/show_product.html', context)

 
    