from django.db import models
from uuid import uuid4
from django.conf import settings
from .product import Product, ProductVariation

class Cart(models.Model):
    """A user's shopping cart, linked to the user and containing multiple CartItems.

    Tracks creation and update timestamps.
    """
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart for {self.user.name}"
    
    def total_items(self):
        """Calculates the total number of items in the cart."""
        return sum(item.quantity for item in self.items.all())
    
    def total_price(self):
        """Calculates the total price of all items in the cart."""
        return sum(item.total_price() for item in self.items.all())
    
    def add_product(self, product, variation=None):
        """Adds a product to the cart, optionally with a specific variation.

        If the product (and variation) already exists in the cart, increments the quantity.
        """
        if variation:
            cart_item, created = CartItem.objects.get_or_create(
                cart=self,
                product=product,
                variation_id=variation,
                defaults={'quantity': 1}
            )
        else:
            cart_item, created = CartItem.objects.get_or_create(
                cart=self,
                product=product,
                variation=None,
                defaults={'quantity': 1}
            )
        
        if not created:
            cart_item.quantity += 1
            cart_item.save()
            
        return cart_item

class CartItem(models.Model):
    """An item in a user's shopping cart, linking to a Product and optional ProductVariation.

    Tracks quantity and timestamps for when the item was added or updated.
    """
    id = models.AutoField(primary_key=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variation = models.ForeignKey(ProductVariation, on_delete=models.SET_NULL, null=True, blank=True)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} for {self.user.name}"
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['cart', 'product', 'variation'], name='unique_cart_item')
        ]
        
    def total_price(self):
        """Calculates the total price for this cart item based on quantity and product/variation price."""
        unit_price = self.variation.price if self.variation else self.product.price
        return unit_price * self.quantity