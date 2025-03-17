from django.urls import path

from .views import *
app_name='inventory'
urlpatterns=[
    # hx-
    path('add-inventory-category/',add_category,name='add_inventory_category'),


    path('',InventoryHome.as_view(),name='inventory'),
    path('get-inventory-categories/',get_inventory_category,name='get_inventory_category'),
]


