
# urls.py
from django.urls import path
from .views import PurchaseOrderListCreateView, PurchaseOrderRetrieveView

urlpatterns = [
    path('purchase_orders/', PurchaseOrderListCreateView.as_view(), name='purchase-order-list-create'),

    path('purchase-orders/<int:id>/', PurchaseOrderRetrieveView.as_view(), name='purchase-order-retrieve'),
]