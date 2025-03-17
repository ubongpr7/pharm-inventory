from django.urls import path
from . import views 
urlpatterns = [
    path('inventories/', views.InventoryCreateAPIView.as_view(), name='inventory-create'),
    path('inventories/list/', views.InventoryListAPIView.as_view(), name='inventory-list'),
    path('inventories/<str:external_system_id>/', views.InventoryDetailAPIView.as_view(), name='inventory-item'),
    path('inventory/<str:pk>/', views.InventoryUpdateView.as_view(), name='inventory-item-update'),

    path('categories/', views.InventoryCategoryListAPIView.as_view(),name='inventory-category-list'),
    path('categories/create/', views.InventoryCategoryCreateView.as_view(),name='inventory-category-list'),
]