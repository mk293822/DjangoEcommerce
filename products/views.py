from django.shortcuts import render
from .models import Department, Product

# Create your views here.
def product_list(request):
    products = Product.objects.all()
    departments = Department.objects.all()
    return render(request, 'products/products_list.html', {'products': products, 'departments': departments})