# views.py
from rest_framework import viewsets, status
from rest_framework.response import Response

from mainapps.common.settings import get_company_or_profile
from ..models import Company, CompanyAddress, Contact
from .serializers import CompanyAddressSerializer, CompanySerializer, ContactSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import RetrieveAPIView
from rest_framework.generics import ListAPIView
from django.core.cache import cache


class CompanyViewSet(viewsets.ModelViewSet):
    serializer_class = CompanySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        company = get_company_or_profile(self.request.user)
        return Company.objects.filter(profile=company)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        company = get_company_or_profile(self.request.user)
        context['company'] = company
        return context

    def perform_create(self, serializer):
        user = self.request.user
        company = get_company_or_profile(self.request.user)

        serializer.save(profile=company, created_by=user)



class CompanyDetailView(RetrieveAPIView):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = [IsAuthenticated]
    lookup_field='pk'




class SupplierListAPIView(ListAPIView):
    serializer_class = CompanySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        company = get_company_or_profile(self.request.user)

        if company:
            user = company.owner
            cache_key = f'supplier_list_{user.id}'
            queryset = cache.get(cache_key)
            print(queryset)
            if queryset is not None:
                return queryset
            else:
                queryset = Company.objects.all()
                queryset = queryset.filter(profile=company).filter(is_supplier=True)
        cache.set(cache_key, queryset, 60 * 15)

        return queryset
    
class CompanyAddressViewSet(viewsets.ModelViewSet):
    serializer_class = CompanyAddressSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        company_id=self.request.GET.get('company_id')
        company= Company.objects.get(id=company_id)
        
        return CompanyAddress.objects.filter(company=company)

class ContactPersonViewSet(viewsets.ModelViewSet):
    serializer_class = ContactSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        try:
            company_id=int(self.request.GET.get('company_id'))
            if company_id ==0:
                print(company_id)
                return None
            
        except:
            return None
        company_id=self.request.GET.get('company_id')
        company= Company.objects.get(id=company_id)
        return Contact.objects.filter(company=company)

        
