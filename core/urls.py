from django.contrib import admin
from django.urls import path,include
from django.urls import re_path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.views.decorators.csrf import csrf_exempt
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)


schema_view = get_schema_view(
   openapi.Info(
      title="Quick Campaign API",
      default_version='v1',
      description="Test description",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="contact@snippets.local"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    # djoser urls
    path('auth-api/', include('djoser.urls')),
    path('', include('djoser.urls.jwt')),
    path('social_auth/', include('djoser.social.urls')),
    #  api endpoints docs
    path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    # path('ses/event-webhook/', SESEventWebhookView.as_view(), name='handle-event-webhook'),


    path('api/v1/accounts/', include("mainapps.accounts.api.urls")),
    path('accounts/', include("mainapps.accounts.urls",namespace='account')),
    path('stock/', include("mainapps.stock.urls",namespace='stock')),
    path('inventory_api/', include("mainapps.inventory.api.urls",)),
    path('inventory/', include("mainapps.inventory.urls",namespace='inventory')),
    path('company/', include("mainapps.company.urls",namespace='company')),
    path('common/', include("mainapps.common.urls",namespace='common')),
    path('common_api/', include("mainapps.common.api.urls")),
    path('management_api/', include("mainapps.management.api.urls")),
    path('management/', include("mainapps.management.urls",namespace='management')),


    # path('permission/', include("mainapps.permit.urls",namespace='permission')),
]