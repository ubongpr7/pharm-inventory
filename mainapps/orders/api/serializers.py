from rest_framework import serializers
from ..models import PurchaseOrder, PurchaseOrderLineItem


class PurchaseOrderLineItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseOrderLineItem
        fields = ['id', 'stock_item', 'quantity', 'unit_price', 'total_price']

class PurchaseOrderSerializer(serializers.ModelSerializer):
    line_items = PurchaseOrderLineItemSerializer(many=True, required=False)

    class Meta:
        model = PurchaseOrder
        
        fields = '__all__'
        read_only_fields = ['id']
        

    def create(self, validated_data):
        line_items_data = validated_data.pop('line_items', [])
        purchase_order = PurchaseOrder.objects.create(**validated_data)
        for line_item_data in line_items_data:
            PurchaseOrderLineItem.objects.create(purchase_order=purchase_order, **line_item_data)
        return purchase_order