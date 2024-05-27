from django.urls import path

from .views import *
app_name='inventory'
urlpatterns=[
    path('',InventoryHome.as_view(),name='inventory'),
]


