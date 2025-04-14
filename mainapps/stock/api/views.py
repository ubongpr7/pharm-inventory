from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from mainapps.inventory.models import Inventory
from mainapps.orders.models import PurchaseOrder, PurchaseOrderStatus
from ..models import StockItem, StockLocation, StockLocationType
from .serializers import StockItemCreateSerializer, StockLocationSerializer, StockLocationTypeSerializer
from rest_framework.response import Response
from rest_framework import generics




class StockLocationViewSet(viewsets.ModelViewSet):
    queryset = StockLocation.objects.all().select_related(
        'official',
        'location_type',
        'profile'
    )
    serializer_class = StockLocationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(
            profile=self.request.user.profile
        )
    def perform_create(self, serializer):
        serializer.save(
            profile=self.request.user.profile,
        )

class StockItemViewSet(viewsets.ModelViewSet):
    queryset = StockItem.objects.all()
    serializer_class = StockItemCreateSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        


        instance = serializer.save(
            # created_by=self.request.user,
            
        )
    def create(self, request, *args, **kwargs):
        reference=request.data.pop('inventory', None)
        try:
            print(reference)
            if reference:
                inventory = Inventory.objects.get(external_system_id=reference)
                request.data['inventory'] = inventory.id
            else:
                print('no reference',reference)
                return
        except Exception as e:
            print('Error',e)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )


class StockLocationTypeViewSet(generics.ListCreateAPIView):
    queryset = StockLocationType.objects.all()
    serializer_class = StockLocationTypeSerializer
    permission_classes = [IsAuthenticated]


