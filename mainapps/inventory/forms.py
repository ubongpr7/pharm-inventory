from django import forms
from .models import Inventory,InventoryCategory
from mainapps.company.models import Company 

class InVentoryForm(forms.ModelForm):
    class Meta:
        model = Inventory
        fields = ['name', 'description', 'category', ]  # include other fields as needed

    # def __init__(self, *args, **kwargs):
    #     user = kwargs.pop('user', None)
    #     super(InVentoryForm, self).__init__(*args, **kwargs)
        

class InventoryCategoryForm(forms.ModelForm):
    name=forms.CharField(max_length=100,required=True,label='Category name*',
    widget=forms.TextInput(
            attrs={
                "hx-get": '/inventory/get-inventory-categories/',
                "hx-target":'#id_parent'
                }
            )
    )
    
    parent=forms.ModelChoiceField(
        queryset=InventoryCategory.objects.none(),
        label='Parent category'
        
    )
    class Meta:
        model = InventoryCategory
        fields = "__all__"

        # fields=['parent']
