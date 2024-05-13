from django.urls import path,include
from rest_framework import routers
from .views import *
router=routers.DefaultRouter()
router.register("user",AuthApi)


urlpatterns=[
    path("",include(router.urls)),
    path("login/",LoginAPIView.as_view(),name="login"),
    path("profile_pic/",ProfilePhotoModelSerialiserView.as_view(),name="profile_pic"),
    path("logout/",LogoutAPI.as_view(),name="logout"),
    path("verify/",VerificationAPI.as_view(),name="verify"),
    path("register/",RegistrationAPI.as_view(),name="register"),
    path("token/",TokenGenerator.as_view(),name="token"),
    path("api_route/",ge_route,name="api_route"),
#    
    ]

