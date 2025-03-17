from rest_framework import serializers
from mainapps.management.models import CompanyProfile,CompanyProfileAddress
from rest_framework import serializers

class CompanyAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyProfileAddress
        fields = '__all__'
        read_only_fields = ['id']

class CompanyProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyProfile
        fields = '__all__'
        read_only_fields = ['id', 'is_verified', 'verification_date', 'created_at', 'updated_at']
