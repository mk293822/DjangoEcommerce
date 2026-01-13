import json
import logging
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from apps.products.models.product import ProductVariation, Product
from apps.products.services.product_details import ProductServices
from .models import Cart, CartItem
from django.template.loader import render_to_string
from django.db import models
from apps.carts.services import CartServices

logger = logging.getLogger(__name__)




# Create your views here.

def carts(request):
    
    if not request.user.is_authenticated:
        return redirect('login')
    
    cart, _ = Cart.objects.get_or_create(user=request.user)
    context = {
        'cart_items': CartServices.get_grouped_cart_items(request.user),
        'total_quantity': cart.total_items,
        'total_price': cart.total_price
    }
    
    return render(request, 'carts/carts.html', context)


# Create your views here.
@csrf_exempt
def add_to_cart(request):
    if request.method != "POST" or not request.user.is_authenticated:
        return JsonResponse({'status': 'error', 'message': 'Unauthorized'}, status=401)

    try:
        data = json.loads(request.body)
        product_id = data.get("product_id")
        requested_quantity = int(data.get('quantity', 1))
        selected_options = data.get("selectedOptions", [])

        product = get_object_or_404(Product, id=product_id)
        if not product.status:
            raise ValueError("Product is suspended!")

        cart, _ = Cart.objects.get_or_create(user=request.user)
        
        variation = None
        if product.variations.exists():
            excluded_variation_ids = cart.items.filter(
                product=product,
                variation__isnull=False,
                variation__stock=models.F('quantity')
            ).values_list('variation_id', flat=True)
            
            pr_variation = selected_options or list(
                ProductServices.get_selected_options(
                    product=product,
                    excluded_variation_ids=excluded_variation_ids,
                    return_ids=True,
                    match_product_price=True,
                ).values()
            )
            variation = ProductVariation.objects.filter(
                variation_type_option=sorted(pr_variation)
            ).first()
            
            if not variation:
                raise ValueError("Selected product options are invalid!")

        cart_item_query = cart.items.filter(product=product)
        product_name = product.name
        if variation:
            cart_item_query = cart_item_query.filter(variation=variation)
            product_name = f"{product.name} ({variation.variation_type_options})"
        cart_item = cart_item_query.first()

        max_addable = (variation.stock if variation else product.stock) - (cart_item.quantity if cart_item else 0)

        if max_addable <= 0:
            if variation:
                raise ValueError("The product with these options is out of stock!")
            else:
                raise ValueError("The product is out of stock!")


        quantity_to_add = min(requested_quantity, max_addable)

        if quantity_to_add < requested_quantity:
            if quantity_to_add == 1:
                message = f"Only 1 unit of '{product_name}' was added due to limited stock. ⚠️"
            else:
                message = f"{quantity_to_add} units of '{product_name}' were added to your cart. ⚠️ Stock is limited. ⚠️"
        else:
            message = f"{quantity_to_add} units of '{product_name}' {'were' if quantity_to_add > 1 else 'was'} added to your cart!"


        # Add to cart
        cart_item_dict = cart.add_product(product, variation=variation, quantity=quantity_to_add)
        cart_item_count = cart.total_items
        cart_item_total_price = cart.total_price
        cart_item = CartItem.objects.filter(id=cart_item_dict['id']).first()
        item = {
            "cart_item": cart_item,
            "options_query": ProductServices.get_query_string(product=cart_item.product, variation=cart_item.variation,)
        }

        html = None
        if cart_item_dict['created']:
            html = render_to_string('components/partials/mini_cart_item.html', {'item': item}, request=request)

        return JsonResponse({
            "status": "success",
            "message": message,
            "cart_item": cart_item_dict,
            "cart_item_count": cart_item_count,
            "cart_item_total_price": cart_item_total_price,
            "html": html
        })

    except ValueError as e:
        return JsonResponse({'status': 'error', 'message': str(e)})
    except Exception as e:
        logger.exception("Error adding product to cart")
        return JsonResponse({'status': 'error', 'message': 'Something went wrong'})
