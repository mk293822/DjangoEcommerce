from django.contrib import admin
from django.urls import path
from django.http import JsonResponse
from products.admin.base import ModelAdmin
from products.forms import ProductVariationForm
from products.models.variation_type import VariationTypeOption
from products.models.department import Category
from products.models.product import ProductVariation, Product
from guardian.shortcuts import get_objects_for_user

@admin.register(ProductVariation)
class ProductVariationAdmin(ModelAdmin):
    list_display = ('product', 'stock', 'price', 'variation_type_options')
    form = ProductVariationForm
    model = ProductVariation
    search_fields = ('product__name',)
    sortable_by = ('product', 'stock', 'price')
    
    def variation_type_options(self, obj):
        options = VariationTypeOption.objects.filter(id__in=obj.variation_type_option)
        return " - ".join([str(option) for option in options])
    
    def has_add_permission(self, request):
        return False
    
    def get_form(self, request, obj =None, **kwargs):
        Form = super().get_form(request, obj, **kwargs)
        
        class FormWithRequest(Form):
            def __init__(self1, *args, **kwargs):
                kwargs['request'] = request
                super().__init__(*args, **kwargs)
                
        return FormWithRequest
                

@admin.register(Product)
class ProductAdmin(ModelAdmin):
    list_display = ('name', 'department', 'category', 'price', 'stock', 'status', 'created_by')
    prepopulated_fields = {'slug': ('name',)}
    exclude = ('created_by',)
    sortable_by = ('name', 'department', 'category', 'price', 'stock', 'status')
    search_fields = ('name', 'description')
    
    class Media:
        js = (
            'admin/js/product_category.js',
        )
        
    def created_by(self, obj):
        return obj.user.name
        
        
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
        