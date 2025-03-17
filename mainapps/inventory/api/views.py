from rest_framework import permissions
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ValidationError
from rest_framework.generics import CreateAPIView,ListAPIView,RetrieveAPIView
from django.utils.text import slugify

from mainapps.common.settings import get_company_or_profile
from ..models import Inventory, InventoryCategory
from .serializers import CreateInventoryCategorySerializer, InventoryCategorySerializer, InventorySerializer
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404

from django.db.models import Count


class InventoryCreateAPIView(CreateAPIView):
    queryset = Inventory.objects.all()
    serializer_class = InventorySerializer
    permission_classes = [permissions.IsAuthenticated]
    

    def perform_create(self, serializer):
        user = self.request.user
        company=get_company_or_profile(user)


        serializer.save(
            created_by=user, 
            updated_by=user,
            profile=company

        )


class InventoryListAPIView(ListAPIView):
    serializer_class = InventorySerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self):
        company=get_company_or_profile(self.request.user)
        queryset = Inventory.objects.all()
        
        if company:
            queryset = queryset.filter(profile=company)
            
        return queryset


class InventoryUpdateView(APIView):
    """
    API endpoint to update an existing inventory item.
    """
    def patch(self, request, pk, format=None):
        """
        Update an inventory item given its ID.
        """
        inventory = get_object_or_404(Inventory, pk=pk)
        serializer = InventorySerializer(inventory, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class InventoryCategoryListAPIView(ListAPIView):
    serializer_class = InventoryCategorySerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self):
        company = get_company_or_profile(self.request.user)
        print(company)
        return InventoryCategory.objects.filter(
            profile=company
        ).annotate(
            inventory_count=Count('inventories')  # Rename annotation to avoid conflict
        ).select_related('parent')
    
class InventoryCategoryCreateView(CreateAPIView):
    serializer_class = CreateInventoryCategorySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        user = self.request.user
        company=get_company_or_profile(user)
        serializer.save(
            profile=company

        )

class InventoryDetailAPIView(RetrieveAPIView):
    queryset = Inventory.objects.all()
    serializer_class = InventorySerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field='external_system_id'

