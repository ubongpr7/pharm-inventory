from django.urls import path,include
from .views import *

urlpatterns=[
    path('verification/',twofa, name='verification'),
    path('send_code',send_code,name='send_code'),
]

