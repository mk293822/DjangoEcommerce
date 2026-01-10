from django.contrib import admin
from apps.products.admin.base import NestedAdmin, NestedAdminInline
from apps.products.forms import VariationTypeForm
from apps.products.models.variation_type import VariationTypeOptionImage, VariationType, VariationTypeOption
from apps.products.services.permission_check import has_permission_to_create
from apps.products.services.product_variation import ProductVariationServices


class VariationTypeOptionImageInline(NestedAdminInline):
    model = VariationTypeOptionImage
    fields = ('image', 'order')
    extra = 0
             
class VariationTypeOptionInline(NestedAdminInline):
    model = VariationTypeOption
    extra = 0
    inlines = [VariationTypeOptionImageInline]

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
            
    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)

        if not hasattr(request, "_variation_created"):
            ProductVariationServices.on_create_option(form.instance.product.id)
            request._variation_created = True
            
    def delete_formset(self, request, formset, queryset):
        for obj in queryset:
            ProductVariationServices.on_delete_option(obj)
        super().delete_formset(request, formset, queryset)

        