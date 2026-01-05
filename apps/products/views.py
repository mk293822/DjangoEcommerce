from django.shortcuts import render
from apps.departments.models import Department
from .models.product import Product
from apps.carts.models import Cart, CartItem

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
        return render(request, "products/components/products_list.html", {"products": products})
    
    return render(request, 'products/home.html', context)

def show_product(request, slug):
    
    product = Product.objects.get(slug=slug)
    
    context = {
        'product': product
    }
    return render(request, 'products/show_product.html', context)

 
    