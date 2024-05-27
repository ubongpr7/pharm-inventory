from django import forms
from .models import Company, Contact, Address
from django.forms.models import inlineformset_factory

class BaseCompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = '__all__'
        # fields = ['name', 'is_owner','description', 'website', 'phone', 'email', 'contact', 'link', 'currency']

class OwnerCompanyForm(BaseCompanyForm):
    class Meta:
        model = Company

        exclude=['is_supplier','is_manufacturer','is_customer','is_patiant']
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.fields['is_owner'].widget = forms.HiddenInput()
        self.fields['is_owner'].initial = True

class SupplierCompanyForm(BaseCompanyForm):
    class Meta:
        model = Company

        exclude=['is_owner','is_manufacturer','is_customer','is_patiant']
    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)
        

        self.fields['is_supplier'].widget = forms.HiddenInput()
        self.fields['is_supplier'].initial = True

class ManufacturerCompanyForm(BaseCompanyForm):

    class Meta:
        model = Company

        exclude=['is_owner','is_supplier','is_customer','is_patiant']
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.fields['is_manufacturer'].widget = forms.HiddenInput()
        self.fields['is_manufacturer'].initial = True
class CustomerCompanyForm(BaseCompanyForm):

    class Meta:
        model = Company

        exclude=['is_owner','is_supplier','is_manufacturer','is_patiant']
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.fields['is_customer'].widget = forms.HiddenInput()
        self.fields['is_customer'].initial = True

class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ['name', 'phone', 'email', 'role']

class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['title', 'primary', 'street', 'city', 'state', 'postal_code', 'country', 'shipping_notes', 'internal_shipping_notes', 'link']

ContactFormSet = inlineformset_factory(Company, Contact, form=ContactForm, extra=1)
AddressFormSet = inlineformset_factory(Company, Address, form=AddressForm, extra=1)

# ContactFormSet = inlineformset_factory(
#     Company, Contact, fields=('name', 'phone', 'email', 'role'), extra=1, can_delete=True
# )

# AddressFormSet = inlineformset_factory(
#     Company, Address, fields=('title', 'primary', 'street', 'city', 'state', 'postal_code', 'country', 'shipping_notes', 'internal_shipping_notes', 'link'), extra=1, can_delete=True
# )