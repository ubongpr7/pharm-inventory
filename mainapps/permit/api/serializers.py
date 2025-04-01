from rest_framework import serializers
from mainapps.accounts.models import User
from mainapps.management.models import StaffGroup
from mainapps.permit.models import CustomUserPermission

class PermissionDetailSerializer(serializers.ModelSerializer):
    has_permission = serializers.BooleanField(read_only=True)
    category = serializers.StringRelatedField()

    class Meta:
        model = CustomUserPermission
        fields = ('codename', 'name', 'description', 'category', 'has_permission')

class UserPermissionUpdateSerializer(serializers.ModelSerializer):
    permissions = serializers.ListField(
        child=serializers.CharField(),
        write_only=True,
        help_text="List of permission codenames to assign"
    )

    class Meta:
        model = User
        fields = ('permissions',)

class GroupPermissionUpdateSerializer(serializers.ModelSerializer):
    permissions = serializers.ListField(
        child=serializers.CharField(),
        write_only=True,
        help_text="List of permission codenames to assign"
    )

    class Meta:
        model = StaffGroup
        fields = ('permissions',)
