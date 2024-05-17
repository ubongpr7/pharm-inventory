from django.urls import path,include
from .views import *
app_name='account'
urlpatterns=[
    path('verification/',twofa, name='verification'),
    path('send_code',send_code,name='send_code'),
    path('register',CreateUser.as_view(),name='register_user'),
]

