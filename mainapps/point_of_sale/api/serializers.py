from rest_framework import serializers
from ..models import (
    POSTerminal, POSSession, POSOrder, POSOrderItem, 
    IntegratedPayment, SyncManager
)
from django.contrib.auth import get_user_model

User = get_user_model()

class POSTerminalSerializer(serializers.ModelSerializer):
    class Meta:
        model = POSTerminal
        fields = ['sync_identifier', 'name', 'location', 'is_online']


class POSSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = POSSession
        fields = [
            'sync_identifier', 'terminal', 'user', 'opening_time', 
            'closing_time', 'opening_balance', 'calculated_balance',
            'discrepancy', 'inventory_snapshot', 'offline_operations',
            'is_synced'
        ]
        read_only_fields = ['inventory_snapshot', 'calculated_balance', 'discrepancy']

    def create(self, validated_data):
        # Ensure inventory snapshot is created
        session = POSSession.objects.create(**validated_data)
        return session


class POSOrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = POSOrderItem
        fields = [
            'sync_identifier', 'stock_item', 'quantity', 
            'captured_price', 'captured_cost', 'tax_profile',
            'line_total'
        ]
        read_only_fields = ['line_total']


class POSOrderSerializer(serializers.ModelSerializer):
    items = POSOrderItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = POSOrder
        fields = [
            'sync_identifier', 'session', 'location', 'created_at',
            'finalized_at', 'total', 'inventory_adjusted',
            'pending_sync_operations', 'items', 'is_synced'
        ]
        read_only_fields = ['created_at', 'finalized_at', 'inventory_adjusted']

    def create(self, validated_data):
        items_data = self.context.get('items', [])
        order = POSOrder.objects.create(**validated_data)
        
        # Create order items
        for item_data in items_data:
            POSOrderItem.objects.create(order=order, **item_data)
            
        # Calculate total
        order.total = sum(item.line_total for item in order.items.all())
        order.save()
        
        return order


class IntegratedPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = IntegratedPayment
        fields = [
            'sync_identifier', 'order', 'payment_method', 
            'amount', 'transaction_ref', 'synced_with_accounting'
        ]


class SyncManagerSerializer(serializers.ModelSerializer):
    class Meta:
        model = SyncManager
        fields = [
            'last_successful_sync', 'pending_operations',
            'sync_state', 'device_identifier'
        ]

