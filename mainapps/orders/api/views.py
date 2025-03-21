from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from ..models import PurchaseOrder
from .serializers import PurchaseOrderSerializer
# from django.core.cache import cache
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
# from django_filters import rest_framework as filters


class PurchaseOrderRetrieveView(generics.RetrieveAPIView):
    queryset = PurchaseOrder.objects.all()
    serializer_class = PurchaseOrderSerializer
    lookup_field = 'id' 
    permission_classes = [IsAuthenticated]
    

class PurchaseOrderCreateView(generics.CreateAPIView):
    queryset = PurchaseOrder.objects.all()
    serializer_class = PurchaseOrderSerializer
    permission_classes = [IsAuthenticated]



# class PurchaseOrderFilter(filters.FilterSet):
#     class Meta:
#         model = PurchaseOrder
#         fields = ['status', 'supplier', 'issue_date']

class PurchaseOrderListCreateView(generics.ListCreateAPIView):
    queryset = PurchaseOrder.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = PurchaseOrderSerializer
    # filter_backends = [filters.DjangoFilterBackend]
    # filterset_class = PurchaseOrderFilter