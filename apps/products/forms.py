
from django import forms
from .models.variation_type import VariationType
from .models.product import Product, ProductVariation

class ProductVariationForm(forms.ModelForm):
    
    variation_type_option_display = forms.CharField(
        label='Variation Type Options',
        required=False,
        disabled=True,
        widget=forms.Textarea()
    )
    
    class Meta:
        model = ProductVariation
        fields = ['product', 'stock', 'price']
        
    
    def __init__(self, *args, **kwargs):
        request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

        variation_types = VariationType.objects.filter(product=self.instance.product)
        
        options = []
        
        for vt in variation_types:
            options.extend(vt.options.filter(
                id__in=self.instance.variation_type_option
            ))
            
        option_display = ""
        for option in options:
            option_display += f"{option.variation_type.name}: {option.name} \n "
            
        self.fields['variation_type_option_display'].initial = option_display
        if request is not None:
            self.fields['product'].queryset = Product.objects.filter(created_by=request.user)
        
        
class VariationTypeForm(forms.ModelForm):
    class Meta:
        model = VariationType
        fields = ['name','type', 'product']
        
    def __init__(self, *args, **kwargs):
        request = kwargs.pop("request", None)
        super().__init__(*args, **kwargs)
        
        if request is not None:
            self.fields['product'].queryset = Product.objects.filter(created_by=request.user)
            