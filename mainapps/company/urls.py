from django.urls import path
from .views import *

app_name='company'

urlpatterns = [
    path('create/<str:company_id>/<str:type>/', CompanyCreateView.as_view(), name='company_create'),
]
