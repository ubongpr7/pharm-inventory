from iso4217 import Currency
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from datetime import date

def validate_currency_code(value):
    try:
        currency = Currency(value)
    except ValueError:
        raise ValidationError(f"{value} is not a valid currency code.")



alphabet_validator = RegexValidator(r'^[a-zA-Z ]*$', 'Only alphabet characters are allowed.')
zip_code_validator = RegexValidator(r'^[0-9]{6}$', 'The zip code should be of the form DDDDDD.')



    
def adult_validator(date_value):
    age = (date.today() - date_value).days / 365
    if age < 18:
        raise ValidationError('You must be at least 18 years old.')


