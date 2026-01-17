from collections import defaultdict
from decimal import Decimal
from apps.products.services.product_details import ProductServices
from .models import Cart, CartItem

class CartServices:
    
    @staticmethod
    def get_cart_context(user):
        
        if not user.is_authenticated:
            return {}
        
        cart, _ = Cart.objects.get_or_create(user=user)
        cart_items = CartItem.objects.filter(cart=cart)
        
        cart_items = [{
            'cart_item': item,
            'options_query': ProductServices.get_query_string(product=item.product, variation=item.variation)
        } for item in cart_items]
        
        return {
            "cart": cart,
            'cart_items': cart_items
        }
        
        
    @staticmethod
    def get_grouped_cart_items(user):
        
        cart, _ = Cart.objects.get_or_create(user=user)
        items = CartItem.objects.filter(cart=cart)
        
        grouped_items = defaultdict(lambda: {
            "items": [],
            "total_quantity": 0,
            "total_price": Decimal('0.00')
        })
        
        for item in items:
            creator = item.product.created_by
            grouped_items[creator.id]["vendor"] = creator
            grouped_items[creator.id]["items"].append({
                "cart_item": item,
                "options_query": ProductServices.get_query_string(
                    product=item.product,
                    variation=item.variation
                ),
            })
            grouped_items[creator.id]["total_quantity"] += item.quantity
            grouped_items[creator.id]["total_price"] += item.total_price()
        
        return dict(grouped_items)