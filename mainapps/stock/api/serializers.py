# serializers.py
from rest_framework import serializers

from mainapps.utils.generators import generate_batch_code
from ..models import StockItem, StockLocation

class StockItemCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating StockItem instances with user-controlled fields"""
    
    class Meta:
        model = StockItem
        fields = [
            'id',
            'inventory',
            'name',
            'created_at',
            'updated_at',
            'quantity',
            'location',
            'parent',
            'serial',
            'batch',
            'packaging',
            'status',
            'expiry_date',
            'purchase_order',
            'sales_order',
            'purchase_price',
            'delete_on_deplete',
            'notes',
            'link',
            'customer',
            'packaging'
            'sku',
        ]

        extra_kwargs = {
            'serial': {'required': False},
            'batch': {'required': False},
            'location': {'required': True},
            'inventory': {'required': True}
        }
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate(self, data):
        """Add custom validation for stock item creation"""
        
        if data['quantity'] <= 0:
            raise serializers.ValidationError("Quantity must be positive")

        return data

