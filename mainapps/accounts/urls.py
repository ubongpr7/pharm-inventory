from django.urls import path,include
from .views import *
app_name='accounts'
urlpatterns=[
    
    path('signout/',signout, name='signout'),
    path('register/',RegisterPage.as_view(), name='register'),
    # path('signin/',signin, name='signin'),
    path('signin/',LoginPage.as_view(), name='signin'),
    path('welcome/',LandingPage.as_view(), name='land'),
    path('verification/',twofa, name='verification'),
    path('send_code',send_code,name='send_code'),
    path('signup',CreateUser.as_view(),name = 'signup'),
]

