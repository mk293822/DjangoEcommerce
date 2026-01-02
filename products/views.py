from django.shortcuts import render
from .models.department import Department
from .models.product import Product
from .models.cart import Cart
from django.http import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt

# Create your views here.
def product_list(request):
    
    products = Product.objects.all()
    departments = Department.objects.filter(status=True)
    
    department_id = request.GET.get('department')
    if department_id == "all" or not department_id:
        products = Product.objects.all()
        selected_department = "all"
    else:
        products = Product.objects.filter(department_id=department_id)
        selected_department = department_id


    return render(request, 'products/products_list.html', {'products': products, 'departments': departments, 'selected_department': selected_department})

@csrf_exempt
def add_to_cart(request):
    if request.method == "POST" and request.user.is_authenticated:
        data = json.loads(request.body)
        product_id = data.get("product_id")
        product_variation = data.get("product_variation")
        product = Product.objects.get(id=product_id)
        cart, _ = Cart.objects.get_or_create(user=request.user)
        cart_item = cart.add_product(product, variation=product_variation)
        
        return JsonResponse({"status": "success", "cart_item": cart_item})
        
        