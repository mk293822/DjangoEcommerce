from django import template

register = template.Library()

@register.filter(name='add_attrs')
def add_attrs(field, attrs):
    attrs_dict = {}
    for attr in attrs.split('|'):
        key, value = attr.split('=')
        attrs_dict[key] = value
        
    return field.as_widget(attrs=attrs_dict)