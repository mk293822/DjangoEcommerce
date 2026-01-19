from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required

from apps.orders.models import Order
# Create your views here.

@login_required(login_url='login')
def checkout_view(request, vendor_id=None):
    
    context = {}
    
    if vendor_id:
        context['vendor_id'] = vendor_id
    
    return render(request, 'orders/checkout.html', context)

@login_required(login_url='login')
def orders(request):
    orders = (
        Order.objects
        .filter(user=request.user)
        .prefetch_related(
            'items__product',
            'items__variation',
        )
    )
    context = {
        'orders': orders,
    }
    return render(request, 'orders/orders.html', context)

@login_required(login_url='login')
def order_details(request, order_id):
    order = get_object_or_404(
        Order.objects.prefetch_related(
            'items__product',
            'items__variation',
        ),
        id=order_id
    )
    context = {
        'order': order,
    }
    
    return render(request, 'orders/order_details.html', context)