from django.shortcuts import render
import json
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from apps.products.models.product import ProductVariation, Product
from .models import Cart, CartItem
from django.template.loader import render_to_string

# Create your views here.

@csrf_exempt
def add_to_cart(request):
    if request.method == "POST" and request.user.is_authenticated:
        data = json.loads(request.body)
        product_id = data.get("product_id")
        product_variation = data.get("product_variation")
        product = Product.objects.get(id=product_id)
        
        if product.status:
            cart, _ = Cart.objects.get_or_create(user=request.user)
            pr_variation = ProductVariation.objects.filter(product=product).first()
            
            cart_item_dict = cart.add_product(product, variation=pr_variation)
            cart_item = CartItem.objects.get(id=cart_item_dict['id'])
            cart_item_count = cart.total_items()
            cart_item_total_price = cart.total_price()
            
            html = None
            if cart_item_dict['quantity'] == 1:
                html = render_to_string('components/partials/mini_cart_item.html', {'item': cart_item}, request=request)
            
            return JsonResponse({
                "status": "success", 
                'cart_item': cart_item_dict, 
                "cart_item_count": cart_item_count,
                "cart_item_total_price": cart_item_total_price,
                "html": html
                })
        
        return JsonResponse({"status": "error",'message': 'Product is suspended!'})
   