from django.forms import ModelForm
from .models import  Inventory


class InVentoryForm(ModelForm):

    class Meta:
        model = Inventory
        fields= '__all__' 

