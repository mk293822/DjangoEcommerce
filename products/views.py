from django.shortcuts import render
from .models.department import Department
from .models.product import Product
from .models.cart import Cart
from django.http import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt

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
            cart_item = cart.add_product(product, variation=product_variation)
            
            return JsonResponse({"status": "success", "cart_item": cart_item})
        
        return JsonResponse({'error': 'Product is suspended!'})