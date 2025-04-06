from rest_framework import serializers
from ..models import PurchaseOrder, PurchaseOrderLineItem

class PurchaseOrderLineItemSerializer(serializers.ModelSerializer):
    stock_item_name= serializers.CharField(source='stock_item.name', read_only=True)
    class Meta:
        model = PurchaseOrderLineItem
        fields = [
            'id',
            'purchase_order',
            'stock_item',
            'stock_item_name',
            'quantity',
            'unit_price',
            'tax_rate',
            'tax_amount',
            'discount_rate',
            'discount',
            'total_price',
        ]
        read_only_fields = ['id','total_price']

class PurchaseOrderSerializer(serializers.ModelSerializer):
    line_items = PurchaseOrderLineItemSerializer(many=True, required=False)

    class Meta:
        model = PurchaseOrder
        fields = '__all__'
        read_only_fields = ['id','line_items']

        
