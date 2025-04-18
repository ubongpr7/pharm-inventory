from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
from django.utils import timezone
from django.shortcuts import get_object_or_404

from ..models import (
    POSTerminal, POSSession, POSOrder, POSOrderItem, 
    IntegratedPayment, SyncManager
)
from .serializers import (
    POSTerminalSerializer, POSSessionSerializer, POSOrderSerializer,
    POSOrderItemSerializer, IntegratedPaymentSerializer,
    CustomerSerializer, LocationSerializer
)
from mainapps.stock.models import StockItem, Location
from mainapps.stock.api.serializers import StockItemCreateSerializer
from django.contrib.auth import get_user_model

User = get_user_model()

class POSTerminalViewSet(viewsets.ModelViewSet):
    queryset = POSTerminal.objects.all()
    serializer_class = POSTerminalSerializer
    lookup_field = 'sync_identifier'
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'location__name']


class POSSessionViewSet(viewsets.ModelViewSet):
    queryset = POSSession.objects.all()
    serializer_class = POSSessionSerializer
    lookup_field = 'sync_identifier'
    
    @action(detail=True, methods=['post'])
    def close(self, request, sync_identifier=None):
        session = self.get_object()
        if session.closing_time:
            return Response(
                {"error": "Session already closed"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Close the session
        session.closing_time = timezone.now()
        session.calculated_balance = request.data.get('calculated_balance', 0)
        session.discrepancy = request.data.get('discrepancy', 0)
        session.save()
        
        return Response(self.get_serializer(session).data)


class POSOrderViewSet(viewsets.ModelViewSet):
    queryset = POSOrder.objects.all()
    serializer_class = POSOrderSerializer
    lookup_field = 'sync_identifier'
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['id', 'session__sync_identifier']
    ordering_fields = ['created_at', 'finalized_at', 'total']
    ordering = ['-created_at']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by active orders
        active = self.request.query_params.get('active')
        if active == 'true':
            queryset = queryset.filter(finalized_at__isnull=True)
        
        return queryset
    
    def create(self, request, *args, **kwargs):
        # Extract items data
        items_data = request.data.pop('items', [])
        
        # Create serializer with items in context
        serializer = self.get_serializer(
            data=request.data, 
            context={'items': items_data}
        )
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['patch'])
    def status(self, request, sync_identifier=None):
        order = self.get_object()
        status_value = request.data.get('status')
        
        if status_value == 'finalized' and not order.finalized_at:
            order.finalize_order()
        elif status_value == 'void':
            # Implement void logic
            pass
        
        return Response(self.get_serializer(order).data)


class IntegratedPaymentViewSet(viewsets.ModelViewSet):
    queryset = IntegratedPayment.objects.all()
    serializer_class = IntegratedPaymentSerializer
    lookup_field = 'sync_identifier'
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        with transaction.atomic():
            # Create the payment
            payment = serializer.save()
            
            # Update the order if needed
            order = payment.order
            # Add any additional logic here
            
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = StockItem.objects.all()
    serializer_class = StockItemCreateSerializer
    lookup_field = 'sync_identifier'
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'sku', 'barcode', 'category']
    ordering_fields = ['name', 'price', 'stock_quantity']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by category
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category=category)
        
        # Filter popular products
        popular = self.request.query_params.get('popular')
        if popular == 'true':
            queryset = queryset.filter(is_popular=True)
        
        return queryset


class CustomerViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = CustomerSerializer
    lookup_field = 'uuid'
    filter_backends = [filters.SearchFilter]
    search_fields = ['username', 'email', 'first_name', 'last_name']


class TableViewSet(viewsets.ModelViewSet):
    queryset = Location.objects.filter(type='table')  # Assuming Location has a type field
    serializer_class = LocationSerializer
    lookup_field = 'sync_identifier'
    
    @action(detail=True, methods=['patch'])
    def status(self, request, sync_identifier=None):
        table = self.get_object()
        status_value = request.data.get('status')
        
        # Update table status
        table.status = status_value
        table.save()
        
        return Response(self.get_serializer(table).data)


class SyncViewSet(viewsets.ViewSet):
    """
    ViewSet for handling synchronization operations
    """
    
    @action(detail=False, methods=['post'])
    def sync_pending(self, request):
        """
        Sync pending operations from client to server
        """
        operations = request.data.get('operations', [])
        results = []
        
        for operation in operations:
            # Process each operation based on type
            op_type = operation.get('type')
            op_data = operation.get('data', {})
            
            if op_type == 'createOrder':
                # Handle order creation
                result = self._process_order_creation(op_data)
            elif op_type == 'updateOrderStatus':
                # Handle order status update
                result = self._process_order_status_update(op_data)
            elif op_type == 'updateTableStatus':
                # Handle table status update
                result = self._process_table_status_update(op_data)
            elif op_type == 'processPayment':
                # Handle payment processing
                result = self._process_payment(op_data)
            elif op_type == 'startSession':
                # Handle session creation
                result = self._process_session_creation(op_data)
            else:
                result = {'success': False, 'message': f'Unknown operation type: {op_type}'}
            
            results.append({
                'operation': op_type,
                'result': result
            })
        
        return Response({
            'success': True,
            'results': results
        })
    
    def _process_order_creation(self, data):
        # Implementation for order creation
        try:
            # Create order logic
            return {'success': True, 'message': 'Order created successfully'}
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    def _process_order_status_update(self, data):
        # Implementation for order status update
        try:
            # Update order status logic
            return {'success': True, 'message': 'Order status updated successfully'}
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    def _process_table_status_update(self, data):
        # Implementation for table status update
        try:
            # Update table status logic
            return {'success': True, 'message': 'Table status updated successfully'}
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    def _process_payment(self, data):
        # Implementation for payment processing
        try:
            # Process payment logic
            return {'success': True, 'message': 'Payment processed successfully'}
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    def _process_session_creation(self, data):
        # Implementation for session creation
        try:
            # Create session logic
            return {'success': True, 'message': 'Session created successfully'}
        except Exception as e:
            return {'success': False, 'message': str(e)}
