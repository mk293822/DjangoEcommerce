from django.contrib import admin
from .models import Cart, CartItem

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    model = Cart
    list_display = ('user', 'cart_item_count')
    
    def cart_item_count(self, obj):
        return obj.items.count()
    
@admin.register(CartItem)
class CartAdmin(admin.ModelAdmin):
    model = CartItem
    list_display = ('product', 'variation', 'quantity')
    