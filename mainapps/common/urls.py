from django.urls import path
from .views import *
app_name='common'
urlpatterns = [
    path('',HomEPage.as_view(),name='home'),
    path('add/<str:app_name>/<str:company_id>/<str:model_name>/', AjaxTabGenericCreateView.as_view(), name='add_item'),
    
    
    ###################################################################################
    # ajax
    path('list/<str:app_name>/<str:company_id>/<str:model_name>/', AjaxGenericList.as_view(), name='item_list'),
    # path('list/<str:app_name>/<str:company_id>/<str:model_name>/', AjaxGenericList.as_view(), name='item_list'),
    # path('add-address/', add_address, name='add_address'),
    path('get-regions/', get_regions, name='get_regions'),
    path('get-subregions/', get_subregions, name='get_subregions'),
    path('get-cities/', get_cities, name='get_cities'),
]
