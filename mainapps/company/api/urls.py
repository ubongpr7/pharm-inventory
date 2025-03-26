# urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views


router = DefaultRouter()
router.register(r'companies', views.CompanyViewSet, basename='company')
router.register(r'company-addresses', views.CompanyAddressViewSet, basename='company-addresses')
router.register(r'company-contacts', views.ContactPersonViewSet, basename='company-contacts')

urlpatterns = [
    path('', include(router.urls)),
    path('suppliers/', views.SupplierListAPIView.as_view(), name='supplier-list'),
    path('company/detail/<str:pk>/', views.CompanyDetailView.as_view(), name='supplier-detail'),
]

