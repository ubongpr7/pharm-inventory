from django.contrib.auth import login as api_login, logout as api_logout
from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.conf import settings


from rest_framework import viewsets
from rest_framework.parsers import FormParser,MultiPartParser,JSONParser,FileUploadParser
from rest_framework.decorators import action,api_view
from rest_framework.request import Request
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework import generics,permissions

from rest_framework_simplejwt.views import TokenObtainPairView

from mainapps.accounts.models import User,VerificationCode,BlacklistedToken
from mainapps.accounts.views import send_html_email
from .serializers import *



class AuthApi(viewsets.ModelViewSet):
    queryset=User.objects.all()
    serializer_class=UserSerializer
    permission_classes=[permissions.IsAuthenticated,]
    # def get_queryset(self):

    #     return User.objects.filter(username=self.request.user.username).first()

class RegistrationAPI(APIView):
    
    def post(self,request):
        serializer=UserRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        user=User.objects.get(username=request.data['username'])
        # request.session['pk']=user.pk
        # request.session["verified "]=False
        return Response({'message':f"User with the email {request.COOKIES.get('email')}  created"},status=201)
    # def get(self,request)

class UploadProfileView(APIView):
    parser_classes=[FileUploadParser]
    def post(self, request ):
        user=request.user
        print(user)
        picture=request.data["file"]
        print(request.data["file"])
        user.picture=picture
        user.save()
        #serializer=UserPictureSerializer(picture,data=request.data)
        if user.picture==picture:
            print("saved")
            return Response("Profile picture updated Successfully",status=200)
        else:
            return Response("Error uploading picture!",status=400)
class LoginAPIView(APIView):
    
    def post(self,request):
        serializer=LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user=serializer.validated_data["user"]
        # session_cookies=request.COOKIES.get('username')
        # request.session['pk']=user.pk
        # request.session["verified "]=False

        return Response("Verify Your Identity",status=200)


@api_view(['GET'])
def ge_route(request):
    route=['/api/token','api/token/refresh']
    return Response(route,status=201)
class VerificationAPI(APIView):
    def get(self,request):
        email=request.COOKIES.get('email')
        get_user=User.objects.get(username=email)
        verified=False
        pk=get_user.pk
        
        if verified:  
            return Response("Authentication Successful",status=200)
        else:
            if pk:
                # print(f'pk: {pk}')
                user =User.objects.get(pk=pk)
                html_file='verify.html'
                to_email=user.email
                from_email= settings.EMAIL_HOST_USER
                code=VerificationCode.objects.get(slug=user.email)
                code.total_attempts+=1
                code.save()
                code=VerificationCode.objects.get(slug=user.email)
                print(f'this is the code: {code}')
                subject=f'Verification code: {code}. {user.first_name} {user.last_name}'
                message= code
                send_html_email(subject, message, from_email, to_email,html_file)
                return Response("Confirmation code has been sent to your registered email",status=200)
    def post(self,request):
        email=request.COOKIES.get('email')
        get_user=User.objects.get(username=email)
        verified=request.COOKIES.get('verified')
        pk=get_user.pk
        user =User.objects.get(pk=pk)
        code=VerificationCode.objects.get(slug=user.email)
        # print(f'this is the code: {code}')
        serializer=VerificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        num=serializer.data['code']        
        if str(code)==str(num):
            # response= RefreshToken.for_user(user=user)
            api_login(request,user)
            response=Response()
            response.data={'message':'Authentication Successful'}
            response.status_code=200
            response.set_cookie(key='pk', value=str(user.pk))
            return response
        else :
            return Response("You have entered an invalid code and therefore need to restart Authentication for security reasons",status=400)
{
    "email":"ubongpr20@gmail.com",
    "username":"ubongpr20@gmail.com",
    "password":"prosuj@Pr20"
}             
        
class TokenGenerator(TokenObtainPairView):
    def post(self, request: Request, *args, **kwargs)  :
        username=request.data.get('username')
        password=request.data.get('password')
        user=authenticate(username=username,password=password)
        if user is not None:
            response=super().post(request,*args,**kwargs)
            response.status_code=200
            return response
        else:
            return Response(status=400)
class UserProfileView(APIView):
    
    permission_classes=[permissions.IsAuthenticated]
    def get(self,request):
        serializer=UserSerializer
        email=request.COOKIES.get('email')
        user=User.objects.get(username=email)
        return Response({'user':user},status=200)

class LogoutAPI(APIView):
    permission_classes=[permissions.IsAuthenticated,]
    def post(self,request):        
        response=Response()
        response.data={
            'message':'Logged Out Successfully'
        }
        response.status_code=200
        api_logout(request)
        return response
    

class ProfilePhotoModelSerialiserView(APIView):
    permission_classes=[permissions.IsAuthenticated]
    parser_classes=[FormParser,MultiPartParser]
    # queryset=ProfilePhoto.objects.all()
    # serializer_class=ProfilePhotoModelSerialiser

    # def create(self, request, *args, **kwargs):
    #     user=request.user
    #     picture=request.data['picture']
    #     ProfilePhoto.objects.create(picture=picture,user=user)
    #     print('done creating')
    #     return Response({'message':'Profile photo uploaded successfully'},status=200)
    def post(self,request,format=None):
        user=request.user
        print(user)
        serializer=ProfilePhotoModelSerialiser(data=request.data,context={'user':user})
        if serializer.is_valid():
            serializer.save()
            print(f'saved {serializer.data}')
            return Response(serializer.data,status=200)
        else:
            print(serializer.errors)
            return Response({'message':'Bad request'},status=500)





