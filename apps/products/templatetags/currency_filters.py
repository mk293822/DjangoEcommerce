from django import template
from apps.products.services.currency_formatter import format_currency

register = template.Library()

@register.filter
def currency(value):
    return format_currency(value)

@register.filter
def quantity(value):
    return range(1, 11 if value > 10 else value + 1)