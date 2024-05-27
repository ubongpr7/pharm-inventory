from django import forms
from .models import Inventory
from mainapps.company.models import Company 

class InVentoryForm(forms.ModelForm):
    class Meta:
        model = Inventory
        fields = ['name', 'description', 'category', 'company']  # include other fields as needed

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(InVentoryForm, self).__init__(*args, **kwargs)
        if user:
            self.fields['company'].queryset = Company.objects.filter(
                is_owner=True,
                created_by=user
            )
