import json
from django.shortcuts import redirect, render
from django.views.generic import TemplateView,ListView,UpdateView
from django.urls import reverse
from django.urls import reverse_lazy
from django.http import HttpResponse, JsonResponse
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
        print(' post')
        form=InventoryCategoryForm(request.POST)
        if form.is_valid():
            print('valid post')
            with transaction.atomic():
                if user.is_main :
                    print('is main')
                    form.instance.profile=user.company
                elif user.is_worker:  
                    print('is worker')
                    form.instance.profile=user.profile
                category=form.save()
                print(category)
                return HttpResponse(
                status=204,
                headers={
                    'HX-Trigger': json.dumps({
                        "bookListChanged": None,
                        "showMessage": f"{category.name} added.",
                    }
                    )
                })
        else:
            return render(request, 'common/inpage_form.html', {
                'form': form,
            })
    else:
        form = InventoryCategoryForm()
    return render(request, 'common/inpage_form.html', {
        'form': form,
    })

                # return JsonResponse({'id':category.id,'name':category.name})

    # return render(request,'common/inpage_form.html',{'form':InventoryCategoryForm})

@login_required
def get_inventory_category(request):
    user= request.user
    if user:
        if user.is_main and user.company:
            categories= InventoryCategory.objects.filter(profile=user.company)
            return render(request,'common/options.html',{'items':categories, 'placeholder' : 'category'})

        elif user.is_worker and user.profile:
            categories= InventoryCategory.objects.filter(profile=user.profile)
            return render(request,'common/options.html',{'items':categories, 'placeholder' : 'category'})
        