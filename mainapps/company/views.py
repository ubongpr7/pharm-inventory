from django.shortcuts import render,redirect
from django.views.generic import CreateView
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse,reverse_lazy
from django.db import transaction
from mainapps.content_type_linking_models.forms import FileFormSet
from mainapps.management.security.encripters import management_dispatch_dispatcher
from middleware.permissions import UserAccessMixins
from django.views.generic.edit import CreateView
from .models import Company
from .forms import *


    


class CompanyCreateView(CreateView,LoginRequiredMixin):
    template_name = 'common/create_inline.html'
    success_url = reverse_lazy('common:home')

    def get_form_class(self):

        if self.kwargs['type'] == 'supplier':
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
        
        if self.kwargs['type']=='supplier Company':
            data['type']= "Supplier"
        elif self.kwargs['type']=='customer':
            data['type']= "Customer "
        elif self.kwargs['type']=='manufacturer':
            data['type']= "Manufacturer Company"
        if self.request.POST:
            data['contacts'] = ContactFormSet(self.request.POST)
            data['addresses'] = AddressFormSet(self.request.POST)
            data['files'] = FileFormSet(self.request.POST)
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
            attachment=Attachment.objects.create(content_object=self.object)
            print(attachment)
            if contacts.is_valid() :
                contacts.instance = self.object
                contacts.save()
                if addresses.is_valid():
                    addresses.instance = self.object
                    addresses.save()
                    
            elif addresses.is_valid():
                addresses.instance = self.object
                addresses.save()
                
            # if self.request.method=="POST":
            #     print('success')
            #     return JsonResponse({'success': True, 'redirect_url': self.success_url})
            return super(CompanyCreateView,self).form_valid(form)
    def dispatch(self, request, *args, **kwargs):
        management_dispatch_dispatcher(self=self,request=request)
        
        return super().dispatch(request, *args, **kwargs)






