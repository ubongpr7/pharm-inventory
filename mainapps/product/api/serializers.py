from rest_framework import serializers

from mainapps.common.models import Attachment
from ..models import *

class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    display_image = serializers.SerializerMethodField()
    pricing_strategy_name = serializers.StringRelatedField(source='pricing_strategy.strategy', read_only=True)
    least_cost_price = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'description', 'base_price', 'category_name',
            'display_image', 'pricing_strategy_name', 'least_cost_price',
            'is_template', 'unit', 'attributes','category'
        ]
        read_only_fields = ['id', 'pricing_strategy_name', 'least_cost_price']
        depth = 1

    def get_least_cost_price(self, obj):
        """Get the minimum price from all variants"""
        try:
            return min(variant.selling_price for variant in obj.variants.all())
        except (ValueError, AttributeError):
            return obj.base_price

    def get_display_image(self, obj):
        """Get image from the variant with lowest price"""
        try:
            # Get the first image of the cheapest variant
            cheapest_variant = min(
                obj.variants.all(),
                key=lambda v: v.selling_price
            )
            
            first_image = cheapest_variant.attachments.filter(
                purpose='MAIN_IMAGE', 
                is_primary=True
            ).first()  
            
            if first_image:
                return self.context['request'].build_absolute_uri(first_image.image.url)
            
            # Fallback to product's default image if exists
            if obj.default_image:
                return self.context['request'].build_absolute_uri(obj.default_image.url)
                
        except (ValueError, AttributeError):
            pass
            
        # Final fallback to placeholder
        return self.context['request'].build_absolute_uri('/static/images/placeholder.jpg')

    # If you need to optimize database queries
    @classmethod
    def setup_eager_loading(cls, queryset):
        """Prefetch related data to avoid N+1 queries"""
        return queryset.prefetch_related(
            'variants',
            'variants__images',
            'category',
            'pricing_strategy'
        )

class VariantAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attachment
        fields = ['id', 'file', 'purpose', 'is_primary', 'description']
        read_only_fields = ['id']

    def validate(self, data):
        if data.get('purpose') == 'MAIN_IMAGE' and not data['file'].name.lower().endswith(('.png', '.jpg', '.jpeg')):
            raise serializers.ValidationError("Main image must be a JPG/PNG file")
        return data

class ProductVariantSerializer(serializers.ModelSerializer):
    attachments = VariantAttachmentSerializer(many=True, read_only=True)
    main_image = serializers.SerializerMethodField()

    class Meta:
        model = ProductVariant
        fields = [
            'id', 'sku', 'attachments', 
            'main_image', 'active', 'variant_number'
        ]
        read_only_fields = ['id','variant_number','sku']

    def get_main_image(self, obj):
        main_image = obj.attachments.filter(
            purpose='MAIN_IMAGE', 
            is_primary=True
        ).first()
        if main_image:
            return self.context['request'].build_absolute_uri(main_image.file.url)
        return None