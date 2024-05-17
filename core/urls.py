from django.contrib import admin
from django.urls import path,include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include("mainapps.accounts.urls",namespace='account')),
    path('stock/', include("mainapps.stock.urls",namespace='stock')),
    path('inventory/', include("mainapps.inventory.urls",namespace='inventory')),
    # path('permission/', include("mainapps.permit.urls",namespace='permission')),
]
