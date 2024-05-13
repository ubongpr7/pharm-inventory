from iso4217 import Currency
from django.core.exceptions import ValidationError

def validate_currency_code(value):
    try:
        currency = Currency(value)
    except ValueError:
        raise ValidationError(f"{value} is not a valid currency code.")
