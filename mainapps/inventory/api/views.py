from rest_framework import permissions
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ValidationError
from rest_framework.generics import CreateAPIView,ListAPIView,RetrieveAPIView,ListCreateAPIView
from django.utils.text import slugify
from django.core.cache import cache
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from django.views.decorators.vary import vary_on_headers
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


# class InventoryListAPIView(ListAPIView):
#     serializer_class = InventorySerializer
#     permission_classes = [permissions.IsAuthenticated]
#     def get_queryset(self):
#         company=get_company_or_profile(self.request.user)
#         queryset = Inventory.objects.all()
        
#         if company:
#             queryset = queryset.filter(profile=company)
            
#         return queryset
#     @method_decorator(cache_page(60 * 15,key_prefix='inventory_list'))
#     @method_decorator(vary_on_headers('Authorization'))
#     def list(self, request, *args, **kwargs):
#         return super().list(request, *args, **kwargs)
    

class InventoryListAPIView(ListAPIView):
    serializer_class = InventorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        company = get_company_or_profile(self.request.user)

        if company:
            user = company.owner
            cache_key = f'inventory_list_{user.id}'
            queryset = cache.get(cache_key)
            print(queryset)
            if queryset is not None:
                return queryset
            else:
                queryset = Inventory.objects.all()
                queryset = queryset.filter(profile=company)


        cache.set(cache_key, queryset, 60 * 15)

        return queryset

    @staticmethod
    def invalidate_cache_for_user(user):
        """
        Invalidate the cache for a specific user.
        """
        cache_key = f'inventory_list_{user.id}'
        cache.delete(cache_key)


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

