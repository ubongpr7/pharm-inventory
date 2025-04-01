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
from mainapps.management.models_activity.activity_logger import log_user_activity
from mainapps.management.models_activity.changes import get_field_changes
from mainapps.permit.models import CombinedPermissions
from ..models import Inventory, InventoryCategory
from .serializers import CreateInventoryCategorySerializer, InventoryCategorySerializer, InventorySerializer
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from mainapps.permit.permit import HasModelRequestPermission

from django.db.models import Count


class InventoryCreateAPIView(CreateAPIView):
    queryset = Inventory.objects.all()
    serializer_class = InventorySerializer
    permission_classes = [permissions.IsAuthenticated,HasModelRequestPermission]
    required_permission= CombinedPermissions.CREATE_INVENTORY

    

    def perform_create(self, serializer):
        user = self.request.user
        company=get_company_or_profile(user)


        serializer.save(
            created_by=user, 
            updated_by=user,
            profile=company

        )
        
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        instance = serializer.instance
        log_user_activity(
            user=request.user,
            action='CREATE',
            instance=instance,
            details={
                'initial_data': request.data,
                'created_data': serializer.data,
                'ip_address': request.META.get('REMOTE_ADDR'),
                'user_agent': request.META.get('HTTP_USER_AGENT')
            },
            async_log=True
        )

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class InventoryListAPIView(ListAPIView):
    serializer_class = InventorySerializer
    permission_classes = [permissions.IsAuthenticated,HasModelRequestPermission]
    required_permission= CombinedPermissions.READ_INVENTORY

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
        original_data = InventorySerializer(inventory).data
        serializer = InventorySerializer(inventory, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            log_user_activity(
                user=request.user,
                action='UPDATE',
                instance=inventory,
                details={
                    'changes': get_field_changes(original_data, serializer.data),
                    'ip_address': request.META.get('REMOTE_ADDR'),
                    'user_agent': request.META.get('HTTP_USER_AGENT')
                },
                async_log=True
            )

            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class InventoryCategoryListAPIView(ListAPIView):
    serializer_class = InventoryCategorySerializer
    permission_classes = [permissions.IsAuthenticated,HasModelRequestPermission]
    required_permission= CombinedPermissions.READ_INVENTORY_CATEGORY
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
    permission_classes = [permissions.IsAuthenticated,HasModelRequestPermission]
    required_permission= CombinedPermissions.CREATE_INVENTORY_CATEGORY
    
    def perform_create(self, serializer):
        user = self.request.user
        company=get_company_or_profile(user)
        serializer.save(
            profile=company

        )
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        instance = serializer.instance
        log_user_activity(
            user=request.user,
            action='CREATE',
            instance=instance,
            details={
                'initial_data': request.data,
                'created_data': serializer.data,
                'ip_address': request.META.get('REMOTE_ADDR'),
                'user_agent': request.META.get('HTTP_USER_AGENT')
            },
            async_log=True
        )

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
class InventoryDetailAPIView(RetrieveAPIView):
    queryset = Inventory.objects.all()
    serializer_class = InventorySerializer
    permission_classes = [permissions.IsAuthenticated,HasModelRequestPermission]
    required_permission= CombinedPermissions.UPDATE_INVENTORY
    lookup_field='external_system_id'

