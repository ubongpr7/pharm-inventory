from django.urls import path,include
from .views import *
app_name='accounts'
urlpatterns=[
    
    path('signout/',signout, name='signout'),
    path('register/',register, name='register'),
    path('signin/',signin, name='signin'),
    path('verification/',twofa, name='verification'),
    path('send_code',send_code,name='send_code'),
    path('signup',CreateUser.as_view(),name = 'signup'),
]

