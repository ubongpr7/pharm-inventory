from django.shortcuts import redirect, render
from django.views.generic import TemplateView,ListView,UpdateView
from django.urls import reverse
from django.urls import reverse_lazy
from django.http import JsonResponse
from .models import Inventory, InventoryCategory
from .forms import InVentoryForm, InventoryCategoryForm
from django.db import transaction
from django.contrib.auth.decorators import login_required




class InventoryHome(TemplateView):
    template_name='inventory/inventory.html'

@login_required
def add_category(request):
    if request.method=='POST':
        user = request.user
        form=InventoryCategoryForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                if user.is_main :
                    form.instance.profile=user.company
                elif user.is_worker:  
                    form.instance.profile=user.profile
                category=form.save()
                return JsonResponse({'id':category.id,'name':category.name})

    return render(request,'common/inpage_form.html',{'form':InventoryCategoryForm})

@login_required
def get_inventory_category(request):
    user= request.user
    if user:
        if user.is_main and user.company:
            categories= InventoryCategory.objects.filter(profile=user.company)
            return render(request,'inventory/categories.html',{'categories':categories})

        elif user.is_worker and user.profile:
            categories= InventoryCategory.objects.filter(profile=user.profile)
            return render(request,'inventory/categories.html',{'categories':categories})
        