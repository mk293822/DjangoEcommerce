from collections import defaultdict
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
        
        grouped_items = defaultdict(list)
        
        for item in items:
            creator = item.product.created_by
            grouped_items[creator].append(item)
        
        return dict(grouped_items)