
from currency_codes import get_all_currencies, Currency
# Assuming you have a default currency code, let's say 'USD'

# Function to get the default currency code
def DEFAULT_CURRENCY_CODE():
    currencies: list[Currency] = get_all_currencies()
    for currency in currencies:
        if currency.code=="USD":


            return (currency.code,'USD')

# # Function to get the currency code mappings for choices
# def currency_code_mappings():
#     # Use iso4217 library to get currency codes and names
#     currencies = [(currency, currency.name.upper()) for currency in Currency]
#     return currencies

def currency_code_mappings():
    currencies: list[Currency] = get_all_currencies()
    # Use iso4217 library to get currency codes and 
    choices = [(currency.code, currency.name.upper()) for currency in currencies]
    return choices

# print(currency_code_default())



