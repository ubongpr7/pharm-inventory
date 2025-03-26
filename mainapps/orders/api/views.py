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
    serializer_class = PurchaseOrderSerializer
    permission_classes = [IsAuthenticated]
    

    def perform_create(self, serializer):
        user = self.request.user


        serializer.save(
            created_by=user, 

        )


from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import status

class PurchaseOrderUpdateView(APIView):
    """
    API endpoint to update an existing inventory item.
    """
    def patch(self, request, pk, format=None):
        """
        Update an inventory item given its ID.
        """
        purchase_order = get_object_or_404(PurchaseOrder, pk=pk)
        serializer = PurchaseOrderSerializer(purchase_order, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PurchaseOrderDetailAPIView(generics.RetrieveAPIView):
    queryset = PurchaseOrder.objects.all()
    serializer_class = PurchaseOrderSerializer
    permission_classes = [IsAuthenticated]
    lookup_field='reference'


class PurchaseOrderListCreateView(generics.ListAPIView):
    queryset = PurchaseOrder.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = PurchaseOrderSerializer
    # filter_backends = [filters.DjangoFilterBackend]
    # filterset_class = PurchaseOrderFilter