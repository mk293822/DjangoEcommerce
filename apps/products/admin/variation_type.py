from django.contrib import admin
from apps.products.admin.base import NestedAdmin, NestedAdminInline
from apps.products.forms import VariationTypeForm
from apps.products.models.variation_type import VariationTypeOptionImage, VariationType, VariationTypeOption
from apps.products.services.permission_check import has_permission_to_create


class VariationTypeOptionImageInline(NestedAdminInline):
    model = VariationTypeOptionImage
    fields = ('image', 'order')
    extra = 0
    
    def save_model(self, request, obj, form, change):
        if not change:
            has_permission_to_create(obj.variation_type_option.variation_type.product.created_by, request.user)
        
        super().save_model(request, obj, form, change)
             
             
class VariationTypeOptionInline(NestedAdminInline):
    model = VariationTypeOption
    extra = 0
    inlines = [VariationTypeOptionImageInline]
    
    def save_model(self, request, obj, form, change):
        if not change:
            has_permission_to_create(obj.variation_type.product.created_by, request.user)
        super().save_model(request, obj, form, change)
        

@admin.register(VariationType)
class VariationTypeAdmin(NestedAdmin):
    form = VariationTypeForm
    list_display = ( 'name', 'type', 'product', 'number_of_options')
    search_fields = ('name', 'product__name')
    sortable_by = ('name', 'type', 'product')
    model = VariationType
    inlines = [VariationTypeOptionInline]
    
    def number_of_options(self, obj):
        return obj.options.count()
    
    def get_form(self, request, obj=None, **kwargs):
        Form = super().get_form(request, obj, **kwargs)
        
        class FormWithRequest(Form):
            def __init__(self1, *args, **fkwargs):
                fkwargs['request'] = request
                super().__init__(*args, **fkwargs)
                
        return FormWithRequest
    
    def save_model(self, request, obj, form, change):
        if not change:
            has_permission_to_create(obj.product.created_by, request.user) 
        super().save_model(request, obj, form, change)
    
