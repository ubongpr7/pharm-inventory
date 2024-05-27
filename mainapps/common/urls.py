from django.urls import path
from .views import *
app_name='common'
urlpatterns = [
    path('',HomEPage.as_view(),name='home'),
    path('add/<str:app_name>/<str:model_name>/', AjaxTabGenericCreateView.as_view(), name='add_item'),
    path('list/<str:app_name>/<str:model_name>/', AjaxGenericList.as_view(), name='item_list'),
]
