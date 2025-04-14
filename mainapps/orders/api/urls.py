
# urls.py
from django.urls import path, include
from .views import (
    ApprovePurchaseOrderView,
    IssuePurchaseOrderView,
    MarkPurchaseOrderCompleteView,
    PurchaseOrderLineItemCreateView,
    PurchaseOrderListCreateView, 
    PurchaseOrderRetrieveView, 
    PurchaseOrderCreateView,
    PurchaseOrderDetailAPIView,
    PurchaseOrderUpdateView,
    ReceivePurchaseOrderView
    )
from  rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'line-item', PurchaseOrderLineItemCreateView, basename='purchase-order-line-item')

urlpatterns = [
    path('', include(router.urls)),
    path('purchase_orders/', PurchaseOrderListCreateView.as_view(), name='purchase-order-list'),
    path('purchase_order/', PurchaseOrderCreateView.as_view(), name='purchase-order-create'),
    path('purchase-order/item/<str:reference>/', PurchaseOrderDetailAPIView.as_view(), name='purchase-order-item'),
    path('purchase-order/update/<str:pk>/', PurchaseOrderUpdateView.as_view(), name='purchase-order-item-update'),
    path('purchase-orders/<int:id>/', PurchaseOrderRetrieveView.as_view(), name='purchase-order-retrieve'),
    
    path('purchase-orders/<int:pk>/approve/', ApprovePurchaseOrderView.as_view(), name='approve-purchase-order'),
    path('purchase-orders/<int:pk>/issue/', IssuePurchaseOrderView.as_view(), name='issue-purchase-order'),
    path('purchase-orders/<int:pk>/receive/', ReceivePurchaseOrderView.as_view(), name='receive-purchase-order'),
    path('purchase-orders/<int:pk>/complete/', MarkPurchaseOrderCompleteView.as_view(), name='complete-purchase-order'),
]