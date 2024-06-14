from django import forms
from cities_light.models import Country, Region, City,SubRegion
from django.urls import reverse, reverse_lazy

from mainapps.content_type_linking_models.forms import AttachmentForm
from mainapps.content_type_linking_models.models import Attachment
from .models import Company, CompanyAddress, Contact 
from django.forms.models import inlineformset_factory

class BaseCompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = '__all__'


class SupplierCompanyForm(BaseCompanyForm):
    class Meta:
        model = Company

        exclude=['is_manufacturer','is_customer','is_patiant']
    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)
        

        self.fields['is_supplier'].widget = forms.HiddenInput()
        self.fields['is_supplier'].initial = True

class ManufacturerCompanyForm(BaseCompanyForm):

    class Meta:
        model = Company

        exclude=['is_supplier','is_customer','is_patiant']
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.fields['is_manufacturer'].widget = forms.HiddenInput()
        self.fields['is_manufacturer'].initial = True
class CustomerCompanyForm(BaseCompanyForm):

    class Meta:
        model = Company

        exclude=['is_supplier','is_manufacturer','is_patiant']
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.fields['is_customer'].widget = forms.HiddenInput()
        self.fields['is_customer'].initial = True

class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ['name', 'phone', 'email', 'role']

class AddressForm(forms.ModelForm):
    country=forms.ModelChoiceField(
        queryset=Country.objects.all(),
        widget=forms.Select(
            attrs={
                "hx-get": '/get-regions/',
                "hx-target":'#id_addresses-0-region'
                }
        )
    )
    region=forms.ModelChoiceField(
        queryset=Region.objects.none(),

        widget=forms.Select(
            attrs={
                "hx-get": '/get-subregions/',
                "hx-target":'#id_addresses-0-subregion'
                }
            )


        )
    subregion=forms.ModelChoiceField(
        queryset=SubRegion.objects.none(),
        widget=forms.Select(
            attrs={
                "hx-get": '/get-cities/',
                "hx-target":'#id_addresses-0-city'
                }
            )
    )
    city=forms.ModelChoiceField(queryset=City.objects.none())
    class Meta:
        model = CompanyAddress
        fields = '__all__'

        # fields = ['title', 'primary','street_number', 'street', 'city', 'state', 'postal_code', 'country', 'shipping_notes', 'internal_shipping_notes', 'link']

ContactFormSet = inlineformset_factory(Company, Contact, form=ContactForm, extra=1)
AddressFormSet = inlineformset_factory(Company, CompanyAddress, form=AddressForm, extra=1)
