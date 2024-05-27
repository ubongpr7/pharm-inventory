from django.shortcuts import redirect, render
from django.views.generic import TemplateView,ListView,UpdateView
from django.urls import reverse
from django.urls import reverse_lazy
from django.http import JsonResponse
from .models import Inventory
from .forms import InVentoryForm




class InventoryHome(TemplateView):
    # model= Inventory()
    template_name='inventory/inventory.html'

    # form_class= InVentoryForm
    # success_url='/admin'