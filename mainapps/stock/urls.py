from django.urls import path
from .views import *
app_name='stock'
urlpatterns=[
    path('create/',CreateStockItem.as_view(),name='create_stockitem'),
    path('add_location/',CreateStockLocation.as_view(),name='add_location'),
]
