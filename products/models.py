from django.db import models
from smart_selects.db_fields import ChainedForeignKey
from django.conf import settings

class Department(models.Model):
    """Represents a top-level product department (e.g., Electronics, Clothing).

    Stores metadata for SEO and a status flag to enable/disable the department.
    """
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    status = models.BooleanField(default=True)
    meta_title = models.CharField(max_length=255, null=True, blank=True)
    meta_description = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
class Category(models.Model):
    """A product category within a Department (e.g., Smartphones in Electronics).

    Categories group related products and reference their parent Department.
    """
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='categories')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Product(models.Model):
    """Product storing core product data: name, description, price and stock.

    Products belong to a Department and Category and can have images and variations.
    """
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=False)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='products')
    category = ChainedForeignKey(Category, on_delete=models.CASCADE, related_name='products', chained_field="department", chained_model_field="department", show_all=False, auto_choose=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(null=True, blank=True)
    status = models.BooleanField(default=False)
    image = models.ImageField(upload_to='product_images/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.name

    
class VariationType(models.Model):
    """Defines a type of variation for a Product (e.g., Size, Color).

    The `type` field can be used to indicate input or presentation details.
    """
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=100)

    def __str__(self):
        return self.name
    
class VariationTypeOption(models.Model):
    """An option/value for a VariationType (e.g., 'Red' for Color, 'XL' for Size).

    Options are tied to a VariationType and used by ProductVariation.
    """
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    variation_type = models.ForeignKey(VariationType, on_delete=models.CASCADE, related_name='options')

    def __str__(self):
        return self.name

class ProductVariationTypeOptionImage(models.Model):
    """An image belonging to a Product Variation Type Options, with optional alt text and display order.

    Images are uploaded to 'product_images/' and can be ordered for presentation.
    """
    id = models.AutoField(primary_key=True)
    variation_type_option = models.ForeignKey(VariationTypeOption, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='product_images/')
    alt_text = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    order = models.PositiveIntegerField(default=0)
    
    
class ProductVariation(models.Model):
    """A concrete product variation linking a Product to a VariationTypeOption.

    Holds variation-specific price and stock information.
    """
    id = models.AutoField(primary_key=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variations')
    variation_type_option = models.ForeignKey(VariationTypeOption, on_delete=models.CASCADE, related_name='product_variations')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.product.name} - {self.variation_type_option.name}"