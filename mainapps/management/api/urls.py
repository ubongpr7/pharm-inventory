from django.urls import path
from .views import CreateCompanyProfileView, CreateCompanyAddressView,OwnerCompanyProfileDetailView


urlpatterns = [
    path('company-profiles/', CreateCompanyProfileView.as_view(), name='create-company-profile'),
    path('company-addresses/', CreateCompanyAddressView.as_view(), name='create-company-address'),
    path('onwnercompany-profile/', OwnerCompanyProfileDetailView.as_view(), name='company-profile-detail'),

]

