# urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import StockItemViewSet, StockLocationTypeViewSet, StockLocationViewSet

router = DefaultRouter()
router.register(r'stock_locations', StockLocationViewSet, basename='stocklocation')
router.register(r'stock_items', StockItemViewSet, basename='stockitem')

urlpatterns = [
    path('', include(router.urls)),
    path('stock_location_types/', StockLocationTypeViewSet.as_view(), name='stocklocationtype'),

]