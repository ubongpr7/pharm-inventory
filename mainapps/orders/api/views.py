from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from mainapps.management.models_activity.changes import get_field_changes
from mainapps.permit.models import CombinedPermissions
from mainapps.permit.permit import HasModelRequestPermission
from middleware import permissions
from ..models import PurchaseOrder
from .serializers import PurchaseOrderSerializer
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from mainapps.management.models_activity.activity_logger import log_user_activity

from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import status


class PurchaseOrderRetrieveView(generics.RetrieveAPIView):
    queryset = PurchaseOrder.objects.all()
    serializer_class = PurchaseOrderSerializer
    lookup_field = 'id' 
    permission_classes = [IsAuthenticated, HasModelRequestPermission]
    required_permission= CombinedPermissions.READ_PURCHASE_ORDER

    

class PurchaseOrderCreateView(generics.CreateAPIView):
    serializer_class = PurchaseOrderSerializer
    permission_classes = [IsAuthenticated, HasModelRequestPermission]
    required_permission= CombinedPermissions.CREATE_PURCHASE_ORDER

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
    

    def perform_create(self, serializer):
        user = self.request.user


        serializer.save(
            created_by=user, 

        )


class PurchaseOrderUpdateView(APIView):
    """
    API endpoint to update an existing inventory item.
    """
    permission_classes = [IsAuthenticated, HasModelRequestPermission]
    required_permission= CombinedPermissions.UPDATE_PURCHASE_ORDER

    def patch(self, request, pk, format=None):
        """
        Update an inventory item given its ID.
        """
        purchase_order = get_object_or_404(PurchaseOrder, pk=pk)
        original_data = PurchaseOrderSerializer(purchase_order).data
        

        serializer = PurchaseOrderSerializer(purchase_order, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            instance = serializer.instance
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
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PurchaseOrderDetailAPIView(generics.RetrieveAPIView):
    queryset = PurchaseOrder.objects.all()
    serializer_class = PurchaseOrderSerializer
    permission_classes = [IsAuthenticated, HasModelRequestPermission]
    required_permission= CombinedPermissions.READ_PURCHASE_ORDER
    lookup_field='reference'


class PurchaseOrderListCreateView(generics.ListAPIView):

    queryset = PurchaseOrder.objects.all()
    serializer_class = PurchaseOrderSerializer
    permission_classes = [IsAuthenticated, HasModelRequestPermission]
    required_permission= CombinedPermissions.READ_PURCHASE_ORDER

    def get_queryset(self):
        return super().get_queryset().filter(inventory__profile=self.request.user.profile)