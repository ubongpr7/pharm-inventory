from iso4217 import Currency

# Assuming you have a default currency code, let's say 'USD'
DEFAULT_CURRENCY_CODE = 'USD'

# Function to get the default currency code
def currency_code_default():
    return DEFAULT_CURRENCY_CODE

# Function to get the currency code mappings for choices
def currency_code_mappings():
    # Use iso4217 library to get currency codes and names
    currencies = [(currency, currency.name) for currency in Currency]
    return currencies
