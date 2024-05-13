from django.contrib import admin
from django.urls import path,include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include("mainapps.accounts.urls")),
    path('permission/', include("mainapps.permit.urls")),
]
