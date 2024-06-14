from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include("mainapps.accounts.urls",namespace='account')),
    path('stock/', include("mainapps.stock.urls",namespace='stock')),
    path('inventory/', include("mainapps.inventory.urls",namespace='inventory')),
    path('company/', include("mainapps.company.urls",namespace='company')),
    path('', include("mainapps.common.urls",namespace='common')),
    path('management/', include("mainapps.management.urls",namespace='management')),
    # path('permission/', include("mainapps.permit.urls",namespace='permission')),
]+static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root = settings.STATIC_URL)
