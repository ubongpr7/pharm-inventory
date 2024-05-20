from django.urls import path

from .views import *
app_name='inventory'
urlpatterns=[
    path('',InventoryHome.as_view(),name='inventory'),
    path('create/',CreateInventory.as_view(),name='create_inventory'),

]