from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    POSTerminalViewSet, POSSessionViewSet, POSOrderViewSet,
    IntegratedPaymentViewSet, ProductViewSet, CustomerViewSet,
    TableViewSet, SyncViewSet
)

router = DefaultRouter()
router.register(r'terminals', POSTerminalViewSet)
router.register(r'sessions', POSSessionViewSet)
router.register(r'orders', POSOrderViewSet)
router.register(r'payments', IntegratedPaymentViewSet)
router.register(r'products', ProductViewSet)
router.register(r'customers', CustomerViewSet)
router.register(r'tables', TableViewSet)
router.register(r'sync', SyncViewSet, basename='sync')

urlpatterns = [
    path('', include(router.urls)),
]
