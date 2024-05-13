from django.shortcuts import render
from django.views.generic import CreateView
from .models import Company
from middleware.permissions import UserAccessMixins
# Create your views here.
class CreateCompany(CreateView,UserAccessMixins):
    model=Company
    template_name='company/create.html'
    success_url='/'

    raise_exception=False
    permission_required=('company.create_company','company.view_company')
    # login_url=''
    redirect_field_name='next'
    permission_denied_message='Access Denied'