from rest_framework import serializers
from ..models import Company, CompanyAddress


class CompanyAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyAddress
        fields = '__all__'
        read_only_fields = ('id', 'company', 'created_at', 'updated_at')

    def validate(self, data):
        company = self.context['request'].user.companyprofile.company
        title = data.get('title')
        
        if CompanyAddress.objects.filter(company=company, title=title).exists():
            raise serializers.ValidationError({'title': 'Address with this title already exists for this company'})
        
        return data


class CompanySerializer(serializers.ModelSerializer):
    company_type=serializers.SerializerMethodField()
    base_currency=serializers.SerializerMethodField()
    class Meta:
        model = Company
        fields = [
            'id', 'name', 'description', 'website', 'phone', 'email', 'link',
            'is_customer', 'is_supplier', 'is_manufacturer', 'currency',
            
            'company_type','short_address','base_currency'
        ]
        read_only_fields = ['id','company_type']
    def get_company_type(self, obj):
        if obj.is_customer:
            return 'Customer'
        elif obj.is_supplier:
            return 'Supplier'
        elif obj.is_manufacturer:
            return 'Manufacturer'
    def get_base_currency(self, obj):
        return obj.currency.code