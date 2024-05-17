from .models import *
from django.forms import ModelForm
registerable_models=[StockLocationType,StockLocation,StockItemTracking,StockItem,]

class StockItemForm(ModelForm):
    
    class Meta:
        model=StockItem
        fields='__all__'
class SalesOrderForm(ModelForm):
    
    class Meta:
        model=SalesOrder
        fields='__all__'
class StockLocationForm(ModelForm):
    
    class Meta:
        model=StockLocation
        fields='__all__'


class StockLocationForm(ModelForm):
    
    class Meta:
        model=StockLocation
        fields='__all__'


