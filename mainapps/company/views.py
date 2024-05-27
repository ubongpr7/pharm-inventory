from django.shortcuts import render,redirect
from django.views.generic import CreateView
from django.http import JsonResponse
from django.urls import reverse
from django.db import transaction
from middleware.permissions import UserAccessMixins
from django.views.generic.edit import CreateView
from .models import Company
from .forms import *


    


class CompanyCreateView(CreateView):
    template_name = 'common/create_inline.html'
    # template_name = 'common/create_inline.html'
    success_url = '/inventory/create/'
    # form_class=OwnerCompanyForm

    def get_form_class(self):
        if self.kwargs['type'] == 'owner':
            return OwnerCompanyForm
        elif self.kwargs['type'] == 'supplier':
            return SupplierCompanyForm
        elif self.kwargs['type'] == 'customer':
            return CustomerCompanyForm
        elif self.kwargs['type'] == 'manufacturer':
            return ManufacturerCompanyForm
        else:
            return BaseCompanyForm

    def get_context_data(self, **kwargs):
        data = super(CompanyCreateView,self).get_context_data(**kwargs)
        data['get_url']='/list/company/company/'
        if self.kwargs['type']=='owner':
            data['type']= "Company"
        if self.kwargs['type']=='supplier Company':
            data['type']= "Supplier"
        if self.kwargs['type']=='customer':
            data['type']= "Customer "
        if self.kwargs['type']=='manufacturer':
            data['type']= "Manufacturer Company"
        if self.request.POST:
            data['contacts'] = ContactFormSet(self.request.POST)
            data['addresses'] = AddressFormSet(self.request.POST)
        else:
            data['contacts'] = ContactFormSet()
            data['addresses'] = AddressFormSet()
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        contacts = context['contacts']
        addresses = context['addresses']
        with transaction.atomic():
            form.instance.created_by = self.request.user
        
            self.object = form.save()
            if contacts.is_valid() :
                contacts.instance = self.object
                contacts.save()
                if addresses.is_valid():
                    addresses.instance = self.object
                    addresses.save()
            elif addresses.is_valid():
                addresses.instance = self.object
                addresses.save()
            if self.request.method=="POST":
                print('success')
                return JsonResponse({'success': True, 'redirect_url': self.success_url})
            return super(CompanyCreateView,self).form_valid(form)




