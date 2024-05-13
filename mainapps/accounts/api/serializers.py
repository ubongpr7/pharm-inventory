from rest_framework import serializers,exceptions
from rest_framework.validators import UniqueValidator
from mainapps.accounts.models import User,ProfilePhoto
from django.contrib.auth import authenticate
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer



class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields="__all__"

class UserRegistrationSerializer(serializers.ModelSerializer):
    email=serializers.EmailField(required=True,validators=[UniqueValidator(queryset=User.objects.all())])
    password=serializers.EmailField(required=True,validators=[UniqueValidator(queryset=User.objects.all())])
    password=serializers.CharField(required=True,write_only=True)
    class Meta:
        model=User
        fields=(
            "email",
            "username",
            "password",
            )
        
        # extra_kwargs={
        #     'password':{'write_only':True}
        # }

    def create(self, validated_data):
        user=User.objects.create(username=validated_data['username'],email=validated_data['email'])
        user.set_password(validated_data['password'])
        user.save()
                          

        # instance=self.Meta.model(validated_data)
        # if password is not None:
        #     instance.set_password(password)
        #     instance.save()
        return user

class UserPictureSerializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields=("picture",)

class LoginSerializer(serializers.Serializer):
    username=serializers.EmailField()
    password=serializers.CharField()
    def validate(self,data):
        username=data.get("username","")
        password=data.get("password","")
        if username and password:
            user=authenticate(username=username,password=password)
            if user is not None:
                if user.is_active:
                    data["user"]=user
                else:
                    message="This account is diabled"
                    raise exceptions.ValidationError(message)
        else:
            message="All fields are required"
            raise exceptions.ValidationError(message)
        return data
    
class VerificationSerializer(serializers.Serializer):
    code=serializers.IntegerField()
    
class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['username'] = user.username
        token['first_name'] = user.first_name
        token['last_name'] = user.last_name
        token['id'] = user.id
        token['id'] = user.email
        
        return token 

class ProfilePhotoModelSerialiser(serializers.ModelSerializer):
    picture=serializers.ImageField()
    user=serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    class  Meta:
        model=ProfilePhoto
        fields=('picture','user',)
    
    
           