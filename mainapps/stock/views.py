from django.shortcuts import render
from .forms import *
from django.views.generic import CreateView
from .models import *

# Create your views here.

class CreateStockLocation(CreateView):

    model= StockLocation
    form_class=StockLocationForm
    template_name='stock/create.html'
    success_url='/'
class CreateStockItem(CreateView):

    model= StockItem
    form_class=StockItemForm
    template_name='stock/create.html'
    success_url='/'