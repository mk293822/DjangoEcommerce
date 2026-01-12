from django.db import models
from uuid import uuid4
from django.conf import settings
from requests import options
from apps.core.services.file_services import FileServices
from apps.departments.models import Department, Category
from django.db.models import Q

def image_upload_to(instance, filename):
    return FileServices.generate_file_path(instance, filename, 'product_images')

class ProductQuerySet(models.QuerySet):
    def active(self):
        return self.filter(status=True)
    
    def search(self, query):
        if not query:
            return self
        
        return self.filter(Q(name__contains=query)|Q(slug__contains=query))

class ProductManager(models.Manager):
    def get_queryset(self):
        return ProductQuerySet(self.model, using=self._db)
    
    def active(self):
        return self.get_queryset().active()
    
    def search(self, query):
        return self.get_queryset().search(query)

class Product(models.Model):
    
    """Product storing core product data: name, description, price and stock.

    Products belong to a Department and Category and can have images and variations.
    """
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    name = models.CharField(max_length=255)    
    slug = models.SlugField(unique=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='products')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(null=True, blank=True)
    status = models.BooleanField(default=True)
    image = models.ImageField(upload_to=image_upload_to, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    
    objects = ProductManager()
     
    def __str__(self):
        return self.name

    class Meta:
        permissions = [
            ('sell_product', 'Can sell product'),
        ]
    
    @property
    def max_quantity(self):
        return min(self.stock, 10)



class ProductVariation(models.Model):
    """
    A concrete product variation linking a Product to a VariationTypeOption.

    Holds variation-specific price and stock information.
    """
    id = models.AutoField(primary_key=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variations')
    variation_type_option = models.JSONField(null=False, blank=False)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.product.name} (Variation #{self.pk})"

    @property
    def variation_type_options(self):
        options = self.get_options()
        return " - ".join(option.name for option in options) if options else self.product.name

    def get_options(self):
        variation_types = self.product.variation_types.all()
        option_ids = self.variation_type_option or []

        options = []
        for vt, option_id in zip(variation_types, option_ids):
            option = vt.options.filter(id=option_id).first()
            if option:
                options.append(option)

        return options

        
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['variation_type_option', 'product'], name='unique_product_variation')
        ]