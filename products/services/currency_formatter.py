from babel.numbers import format_currency as babel_format_currency
from django.conf import settings

def format_currency(amount):
    if amount is None:
        amount = 0
    try:
        return babel_format_currency(amount, settings.CURRENCY_FORMAT, locale=settings.CURRENCY_LOCALE)
    except Exception:
        return f"{settings.CURRENCY_FORMAT} {amount:,.2f}"
