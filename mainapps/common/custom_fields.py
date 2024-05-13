from django.db import models
from django.core.validators import MinValueValidator

class MoneyField(models.DecimalField):
    def __init__(self, *args, **kwargs):
        kwargs['max_digits'] = 19  # Adjust this based on your requirements
        kwargs['decimal_places'] = 2  # Adjust this based on your requirements
        kwargs['validators'] = [MinValueValidator(0)]  # Ensure the money value is non-negative
        super().__init__(*args, **kwargs)

