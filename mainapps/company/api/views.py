# views.py
from rest_framework import viewsets, status
from rest_framework.response import Response

from mainapps.common.settings import get_company_or_profile
from ..models import Company, CompanyAddress
from .serializers import CompanyAddressSerializer, CompanySerializer
from rest_framework.permissions import IsAuthenticated


# class CompanyAddressViewSet(viewsets.ModelViewSet):
#     serializer_class = CompanyAddressSerializer
#     permission_classes = [IsAuthenticated]

#     def get_queryset(self):
#         return CompanyAddress.objects.filter(company__profile=self.request.user.companyprofile)

#     def perform_create(self, serializer):
#         company = self.request.user.companyprofile.company
#         serializer.save(company=company)

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
