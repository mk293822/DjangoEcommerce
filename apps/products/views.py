import json
from django.shortcuts import render, get_object_or_404
from apps.carts.models import Cart
from apps.carts.services import CartServices
from apps.departments.models import Department
from apps.products.models.variation_type import VariationType
from apps.products.services.product_details import ProductServices
from .models.product import Product, ProductVariation
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.db.models import Q

# Create your views here.
def product_list(request):
    
    query = request.GET.get('q', '')
    department_id = request.GET.get('department', 'all')
    products: Product = Product.objects.active().order_by('-id')
    departments = Department.objects.filter(status=True)
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
    else:
        cart = None

    if department_id != "all":
        products = products.filter(department_id=department_id)
        
    products = products.search(query)
    products_context = ProductServices.get_product_context(products, cart)
    
    context = {
        'products_context': products_context, 
        'departments': departments, 
        'selected_department': department_id, 
        'query': query,
    } 
    context.update(CartServices.get_cart_context(request.user))        

    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return render(request, "products/components/products_list.html", {"products_context": products_context})
    
    return render(request, 'products/home.html', context)

def product_details(request, slug):
    
    product: Product = get_object_or_404(Product, slug=slug)
    product_variations: ProductVariation = product.variations.all()
    has_variation: bool = product_variations.count() > 0
    variation_types: VariationType = VariationType.objects.filter(product=product)
    carousel_images = ProductServices.get_carousel_images(has_variation, product, request)
    products =  Product.objects.active().filter(Q(department=product.department) | Q(category=product.category)).exclude(id=product.id)
    
    context = {
        'product': product,
        'has_variation': has_variation,
        'carousel_images': carousel_images,
        'created_by': product.created_by.name,
        'quantity': range(1, product.max_quantity + 1),
        'related_products': ProductServices.get_product_context(products, request.user.cart)
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

 
    
