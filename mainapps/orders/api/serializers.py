from rest_framework import serializers
from ..models import PurchaseOrder, PurchaseOrderLineItem

class PurchaseOrderLineItemSerializer(serializers.ModelSerializer):

    stock_item_name= serializers.CharField(source='stock_item.name', read_only=True)
    quantity_w_unit = serializers.SerializerMethodField()
    
    
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
            'quantity_w_unit',
        ]
        read_only_fields = ['id','total_price','quantity_w_unit']
    def get_quantity_w_unit(self, obj):
        if obj.purchase_order:
            return f"{obj.quantity} {obj.stock_item.variant.product.unit.abbreviated_name}"
        return obj.quantity
        

class PurchaseOrderSerializer(serializers.ModelSerializer):
    
    
    class Meta:
        model = PurchaseOrder
        fields = '__all__'
        read_only_fields = ['id',]
    
        
