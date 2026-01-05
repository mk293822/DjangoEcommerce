from django.contrib import admin
from .models import Cart, CartItem

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    model = Cart
    
@admin.register(CartItem)
class CartAdmin(admin.ModelAdmin):
    model = CartItem