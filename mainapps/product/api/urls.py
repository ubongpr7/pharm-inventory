from django.urls  import path,include
from . import views
from rest_framework.routers import DefaultRouter


router= DefaultRouter()
router.register('products',views.ProductViewSet,basename='product')
router.register('productvariant',views.ProductVariantViewSet,basename='productvariant')
router.register('categories',views.ProductCategoryViewSet,basename='productcategory')
urlpatterns = [
    path('',include(router.urls)),
    
]
