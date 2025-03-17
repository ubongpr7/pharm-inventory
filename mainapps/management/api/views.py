from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from mainapps.management.models import CompanyProfile
from .serializers import CompanyProfileSerializer,CompanyAddressSerializer
from rest_framework import generics, permissions

class CreateCompanyAddressView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        company_id = request.data.pop('company', None)
        try:
            company = CompanyProfile.objects.get(id=company_id, owner=request.user)
        except CompanyProfile.DoesNotExist:
            return Response(
                {"detail": "Company not found or you do not have permission to add an address for this company."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = CompanyAddressSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            company.headquarters_address = serializer.instance
            company.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CreateCompanyProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        # Check if the user is a main user
        if not request.user.is_main:
            return Response(
                {"detail": "Only main users can create a company profile."},
                status=status.HTTP_403_FORBIDDEN,
            )

        request.data['owner'] = request.user.id

        serializer = CompanyProfileSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class OwnerCompanyProfileDetailView(generics.RetrieveAPIView):
    serializer_class = CompanyProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        print(self.request.user)
        return get_object_or_404(CompanyProfile, owner=self.request.user)
    
