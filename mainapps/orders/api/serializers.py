from rest_framework import serializers
from ..models import PurchaseOrder, PurchaseOrderLineItem


class PurchaseOrderLineItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseOrderLineItem
        fields = ['id', 'stock_item', 'quantity', 'unit_price', 'total_price']

class PurchaseOrderSerializer(serializers.ModelSerializer):
    # line_items = PurchaseOrderLineItemSerializer(many=True, required=False)

    class Meta:
        model = PurchaseOrder
        
        fields = '__all__'
        read_only_fields = ['id']
        
