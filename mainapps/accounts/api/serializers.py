from rest_framework import serializers,exceptions
from rest_framework.validators import UniqueValidator
from mainapps.accounts.models import User
from django.contrib.auth import authenticate
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from django.contrib.auth.password_validation import validate_password


class RootUserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True,)
    re_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('first_name', 'email', 'password', 're_password')
        extra_kwargs = {
            'first_name': {'required': True},
            'email': {'required': True}
        }


    def create(self, validated_data):
        re_password = validated_data.pop("re_password", None)
        
        user = User.objects.create_user(**validated_data)
        user.is_main=True
        user.save()

    

        return user


class LogoutSerializer(serializers.Serializer):
    refresh=serializers.CharField()

class MyUserSerializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields="__all__"

class UserPictureSerializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields=("picture",)
    
class VerificationSerializer(serializers.Serializer):
    code=serializers.IntegerField()
    
class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    
    
    def validate(self, attrs):
        data = super().validate(attrs)
        user = self.user  
        try:
            company_id = user.company.id
        except user._meta.get_field("company").related_model.DoesNotExist:
            company_id = None
        data.update({
            'id': user.id,
            'username': user.username,
            'is_worker': user.is_worker,
            'is_main': user.is_main,
            'is_verified': user.is_verified,
            'profile': user.profile.id if user.profile else None,
            'email': user.email,
            'company': company_id,
            'first_name': user.first_name,
        })
        
        return data 
    
           