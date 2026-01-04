from django.shortcuts import render
from .models.department import Department
from .models.product import Product
from .models.cart import Cart, CartItem
from django.http import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt
from django.template.loader import render_to_string

# Create your views here.
def product_list(request):
    
    query = request.GET.get('q', '')
    department_id = request.GET.get('department', 'all')
    products = Product.objects.active()
    departments = Department.objects.filter(status=True)
    
    if department_id != "all":
        products = products.filter(department_id=department_id)
        
    products = products.search(query)
    
    context = {
        'products': products, 
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
        return render(request, "products/partials/products_list.html", {"products": products})
    
    return render(request, 'products/home.html', context)

@csrf_exempt
def add_to_cart(request):
    if request.method == "POST" and request.user.is_authenticated:
        data = json.loads(request.body)
        product_id = data.get("product_id")
        product_variation = data.get("product_variation")
        product = Product.objects.get(id=product_id)
        
        if product.status:
            cart, _ = Cart.objects.get_or_create(user=request.user)
            cart_item_dict = cart.add_product(product, variation=product_variation)
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