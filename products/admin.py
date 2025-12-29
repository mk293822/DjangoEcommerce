from django.urls import path
from django.contrib import admin
from django.http import JsonResponse
import nested_admin

from products.forms import ProductVariationForm
from .models import Department, Category, Product, ProductVariation, ProductVariationTypeOptionImage, VariationType, VariationTypeOption

class CategoryInline(admin.TabularInline):
    model = Category
    extra = 0
    
@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'status', 'meta_title', 'numbers_of_categories')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [CategoryInline]
    search_fields = ('name', 'slug')
    sortable_by = ('name', 'slug', 'status', 'numbers_of_categories')

    def numbers_of_categories(self, obj):
        return obj.categories.count()

class VariationTypeOptionImageInline(nested_admin.NestedTabularInline):
    model = ProductVariationTypeOptionImage
    fields = ('image', 'order')
    extra = 0

class VariationTypeOptionInline(nested_admin.NestedTabularInline):
    model = VariationTypeOption
    extra = 0
    inlines = [VariationTypeOptionImageInline]
    
@admin.register(VariationType)
class VariationTypeAdmin(nested_admin.NestedModelAdmin):
    list_display = ( 'name', 'type', 'product', 'number_of_options')
    search_fields = ('name', 'product__name')
    sortable_by = ('name', 'type', 'product')
    model = VariationType
    inlines = [VariationTypeOptionInline]
    
    def number_of_options(self, obj):
        return obj.options.count()
    
@admin.register(ProductVariation)
class ProductVariationAdmin(admin.ModelAdmin):
    list_display = ('product', 'stock', 'price', 'variation_type_options')
    form = ProductVariationForm
    model = ProductVariation
    search_fields = ('product__name',)
    sortable_by = ('product', 'stock', 'price')
    
    def variation_type_options(self, obj):
        options = VariationTypeOption.objects.filter(id__in=obj.variation_type_option)
        return "-".join([str(option) for option in options])
    
    def has_add_permission(self, request):
        return False

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'department', 'category', 'price', 'stock', 'status', 'created_at')
    prepopulated_fields = {'slug': ('name',)}
    exclude = ('created_by',)
    sortable_by = ('name', 'department', 'category', 'price', 'stock', 'status', 'created_at')
    search_fields = ('name', 'description')
    
    class Media:
        js = (
            'admin/js/product_category.js',
        )
        
    def get_urls(self):
        urls = super().get_urls()
        
        custom_urls = [
            path('load-categories/', self.admin_site.admin_view(self.load_categories), name='load_categories'),
        ]
        
        return custom_urls + urls
            
    def load_categories(self, request):
        department_id = request.GET.get('department_id')
        categories = Category.objects.filter(department_id=department_id).values('id', 'name')
        return JsonResponse(list(categories), safe=False)
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        return super().save_model(request, obj, form, change)