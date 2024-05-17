from django.shortcuts import render
from .models import Inventory
from .forms import InVentoryForm
from django.views.generic import CreateView
# Create your views here.

class CreateInventory(CreateView):

    model= Inventory()
    template_name='inventory/create.html'
    form_class= InVentoryForm
    success_url='/admin'