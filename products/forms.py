
import dis
from django import forms
from .models import ProductVariation, VariationType


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
        