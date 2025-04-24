# views.py
from rest_framework import viewsets, status
from rest_framework.response import Response
from mainapps.management.models_activity.changes import get_field_changes
from mainapps.common.settings import get_company_or_profile
from mainapps.permit.models import CombinedPermissions
from mainapps.permit.permit import HasModelRequestPermission
from ..models import Company, CompanyAddress, Contact
from .serializers import CompanyAddressSerializer, CompanySerializer, ContactSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import RetrieveAPIView
from rest_framework.generics import ListAPIView
from django.core.cache import cache
from mainapps.management.models_activity.activity_logger import log_user_activity


class CompanyViewSet(viewsets.ModelViewSet):
    serializer_class = CompanySerializer
    permission_classes = [IsAuthenticated,HasModelRequestPermission]
    required_permission = {
        'create': CombinedPermissions.CREATE_COMPANY,
        'list': CombinedPermissions.READ_COMPANY,
        'retrieve':CombinedPermissions.READ_COMPANY,
        'update': CombinedPermissions.UPDATE_COMPANY,
        'partial_update':CombinedPermissions.UPDATE_COMPANY,
        'destroy': CombinedPermissions.DELETE_COMPANY

    }

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
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        original_data = self.get_serializer(instance).data

        serializer = self.get_serializer(instance, data=request.data, 
                                       partial=kwargs.pop('partial', False))
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}

        log_user_activity(
            user=request.user,
            action='UPDATE',
            instance=instance,
            details={
                'changes': get_field_changes(original_data, serializer.data),
                'ip_address': request.META.get('REMOTE_ADDR'),
                'user_agent': request.META.get('HTTP_USER_AGENT')
            },
            async_log=True
        )

        return Response(serializer.data)
    
    def partial_update(self, request, *args, **kwargs):
        # Reuse the update method with partial=True
        return self.update(request, *args, **kwargs)



class CompanyDetailView(RetrieveAPIView):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = [IsAuthenticated,HasModelRequestPermission]
    required_permission= CombinedPermissions.READ_COMPANY
    lookup_field='pk'

class SupplierListAPIView(ListAPIView):
    serializer_class = CompanySerializer
    permission_classes = [IsAuthenticated,HasModelRequestPermission]
    required_permission= CombinedPermissions.READ_COMPANY

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
    permission_classes = [IsAuthenticated,HasModelRequestPermission]
    required_permission = {
        'create': CombinedPermissions.CREATE_COMPANY_ADDRESS,
        'list': CombinedPermissions.READ_COMPANY_ADDRESS,
        'retrieve':CombinedPermissions.READ_COMPANY_ADDRESS,
        'update': CombinedPermissions.UPDATE_COMPANY_ADDRESS,
        'partial_update':CombinedPermissions.UPDATE_COMPANY_ADDRESS,
        'destroy': CombinedPermissions.DELETE_COMPANY_ADDRESS,
    }

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
    


    def get_queryset(self):
        company_id=self.request.GET.get('company_id')
        company= Company.objects.get(id=company_id)
        
        return CompanyAddress.objects.filter(company=company)
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        original_data = self.get_serializer(instance).data

        serializer = self.get_serializer(instance, data=request.data, 
                                       partial=kwargs.pop('partial', False))
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}

        log_user_activity(
            user=request.user,
            action='UPDATE',
            instance=instance,
            details={
                'changes': get_field_changes(original_data, serializer.data),
                'ip_address': request.META.get('REMOTE_ADDR'),
                'user_agent': request.META.get('HTTP_USER_AGENT')
            },
            async_log=True
        )

        return Response(serializer.data)
    
    def partial_update(self, request, *args, **kwargs):
        # Reuse the update method with partial=True
        return self.update(request, *args, **kwargs)


class ContactPersonViewSet(viewsets.ModelViewSet):
    serializer_class = ContactSerializer
    permission_classes = [IsAuthenticated,HasModelRequestPermission]
    required_permission = {
        'create': CombinedPermissions.CREATE_CONTACT,
        'list': CombinedPermissions.READ_CONTACT,
        'retrieve':CombinedPermissions.READ_CONTACT,
        'update': CombinedPermissions.UPDATE_CONTACT,
        'partial_update':CombinedPermissions.UPDATE_CONTACT,
        'destroy': CombinedPermissions.DELETE_CONTACT
    }


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

        
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        original_data = self.get_serializer(instance).data

        serializer = self.get_serializer(instance, data=request.data, 
                                       partial=kwargs.pop('partial', False))
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}

        log_user_activity(
            user=request.user,
            action='UPDATE',
            instance=instance,
            details={
                'changes': get_field_changes(original_data, serializer.data),
                'ip_address': request.META.get('REMOTE_ADDR'),
                'user_agent': request.META.get('HTTP_USER_AGENT')
            },
            async_log=True
        )

        return Response(serializer.data)
    
    def partial_update(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

