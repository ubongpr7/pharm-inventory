from rest_framework import serializers
from mainapps.common.models import TypeOf, Unit
from mainapps.inventory.models import Inventory, InventoryCategory
from django.utils.translation import gettext_lazy as _

from mainapps.management.models import( 
    ExpirePolicies, 
    ForecastMethods, 
    NearExpiryActions, 
    RecallPolicies, 
    ReorderStrategies
)
class InventorySerializer(serializers.ModelSerializer):
    # Add explicit field declarations for foreign keys
    inventory_type = serializers.PrimaryKeyRelatedField(
        queryset=TypeOf.objects.filter(which_model='inventory'),
        error_messages={'does_not_exist': _('Invalid inventory type')}
    )
   
    category = serializers.PrimaryKeyRelatedField(
        queryset=InventoryCategory.objects.all(),
        required=False,
        allow_null=True
    )
    unit = serializers.PrimaryKeyRelatedField(
        queryset=Unit.objects.all(),
        required=False,
        allow_null=True
    )
    category_name = serializers.CharField(source='category.name', read_only=True)
    unit_name = serializers.CharField(source='unit.name', read_only=True)
    recall_policy_name = serializers.SerializerMethodField()  # Add this field
    reorder_strategy_name = serializers.SerializerMethodField()
    expiration_policy_name = serializers.SerializerMethodField()
    forecast_method_name = serializers.SerializerMethodField()

    class Meta:
        model = Inventory
        fields = [

            'id','name','external_system_id','unit_name', 'description', 'inventory_type', 
              'category','category_name', 'unit',
            'minimum_stock_level', 're_order_point', 're_order_quantity', 'alert_threshold',
            'safety_stock_level', 'supplier_lead_time', 'internal_processing_time',
            'expiration_threshold', 'holding_cost_per_unit', 'ordering_cost',
            'stockout_cost', 'automate_reorder',
            'batch_tracking_enabled','recall_policy_name', 'expiration_policy', 'recall_policy',
            'forecast_method_name','expiration_policy_name','reorder_strategy_name',
            'reorder_strategy', 'forecast_method', 'created_at', 'updated_at'
        ]
        extra_kwargs = {
            'name': {'help_text': _("Unique identifier for this inventory system")},
            'minimum_stock_level': {'min_value': 0},
            're_order_point': {'min_value': 0},
            're_order_quantity': {'min_value': 1},
            'updated_at': {'read_only': True},
            'created_at': {'read_only': True},
            'id': {'read_only': True},
            'unit_name': {'read_only': True},
            'external_system_id': {'read_only': True},
            'recall_policy_name': {'read_only': True},
            'forecast_method_name': {'read_only': True},
            'expiration_policy_name': {'read_only': True},
            'reorder_strategy_name': {'read_only': True},
        }
    def get_recall_policy_name(self, obj):
        return RecallPolicies(obj.recall_policy).label if obj.recall_policy else None

    def get_reorder_strategy_name(self, obj):
        return ReorderStrategies(obj.reorder_strategy).label if obj.reorder_strategy else None

    def get_expiration_policy_name(self, obj):
        return ExpirePolicies(obj.expiration_policy).label if obj.expiration_policy else None

    def get_forecast_method_name(self, obj):
        return ForecastMethods(obj.forecast_method).label if obj.forecast_method else None
    

class InventoryCategorySerializer(serializers.ModelSerializer):
    parent = serializers.SlugRelatedField(
        slug_field='name',
        read_only=True
        # queryset=InventoryCategory.objects.all(),
    )
    inventory_count = serializers.IntegerField(read_only=True)  # Match renamed annotation

    class Meta:
        model = InventoryCategory
        fields = ['id', 'name', 'inventory_count', 'description', 'parent']
        read_only_fields = ['id', 'slug']

class CreateInventoryCategorySerializer(serializers.ModelSerializer):
    parent = serializers.SlugRelatedField(
        slug_field='id',
        required=False,
        allow_null=True,
        queryset=InventoryCategory.objects.all(),
    )
    inventory_count = serializers.IntegerField(read_only=True)  # Match renamed annotation

    class Meta:
        model = InventoryCategory
        fields = ['id', 'name', 'inventory_count', 'description', 'parent']
        read_only_fields = ['id', 'slug']
        depth=1
