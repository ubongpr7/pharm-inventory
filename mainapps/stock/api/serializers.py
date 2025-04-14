# serializers.py
from rest_framework import serializers

from mainapps.utils.generators import generate_batch_code
from ..models import StockItem, StockLocation,StockLocationType
# serializers.py
from rest_framework import serializers

class StockLocationTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockLocationType
        fields = '__all__'
        
class StockLocationSerializer(serializers.ModelSerializer):
    parent = serializers.PrimaryKeyRelatedField(
        queryset=StockLocation.objects.all(),
        allow_null=True,
        required=False
    )
    
    location_type = serializers.PrimaryKeyRelatedField(
        queryset=StockLocationType.objects.all(),
        allow_null=True,
        required=False
    )

    class Meta:
        model = StockLocation
        fields = [
            'id',
            'created_at',
            'updated_at',
            'name',
            'code',
            'official',
            'structural',
            'parent',
            'external',
            'location_type',
            'lft',
            'rght',
            'tree_id',
            'level',
            'description',
        ]
        read_only_fields = [
            'id',
            'created_at',
            'updated_at',
            'lft',
            'rght',
            'tree_id',
            'level',
            'code',
        ]
        
class StockItemCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating StockItem instances with user-controlled fields"""
    quantity_w_unit = serializers.SerializerMethodField()
    
    class Meta:
        model = StockItem
        fields = [
            'id',
            'inventory',
            'name',
            'quantity_w_unit',
            'created_at',
            'updated_at',
            'quantity',
            'location',
            'parent',
            'serial',
            'batch',
            'notes',
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
            'packaging',
            'sku',
        ]

        extra_kwargs = {
            'serial': {'required': False},
            'batch': {'required': False},
            'location': {'required': True},
        }
        read_only_fields = ['id', 'created_at', 'updated_at','quantity_w_unit']

    def get_quantity_w_unit(self, obj):
            if obj.inventory:
                return f"{obj.quantity} {obj.inventory.unit.abbreviated_name}"
            return obj.quantity