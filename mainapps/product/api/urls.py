from django.urls  import path,include
from . import views
from rest_framework.routers import DefaultRouter


router= DefaultRouter()
router.register('product',views.ProductViewset,basename='product')
router.register('productvariant',views.ProductVariantViewset,basename='productvariant')
urlperttterns = [
    path('',include(router.urls)),
    
]
