
# urls.py
from django.urls import path
from .views import (
    PurchaseOrderListCreateView, 
    PurchaseOrderRetrieveView, 
    PurchaseOrderCreateView,
    PurchaseOrderDetailAPIView,
    PurchaseOrderUpdateView
    )


urlpatterns = [
    path('purchase_orders/', PurchaseOrderListCreateView.as_view(), name='purchase-order-list'),
    path('purchase_order/', PurchaseOrderCreateView.as_view(), name='purchase-order-create'),
    path('purchase-order/item/<str:reference>/', PurchaseOrderDetailAPIView.as_view(), name='inventory-item'),
    path('purchase-order/update/<str:pk>/', PurchaseOrderUpdateView.as_view(), name='inventory-item-update'),

    path('purchase-orders/<int:id>/', PurchaseOrderRetrieveView.as_view(), name='purchase-order-retrieve'),
]