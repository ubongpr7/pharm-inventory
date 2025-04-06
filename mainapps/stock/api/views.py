from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets

from mainapps.inventory.models import Inventory
from ..models import StockItem
from .serializers import StockItemCreateSerializer
from mainapps.utils.generators import generate_batch_code, generate_serial_number  

class StockItemCreateAPI(viewsets.ModelViewSet):
    queryset = StockItem.objects.all()
    serializer_class = StockItemCreateSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        reference=self.request.query_params.get('reference')
        if reference:
            inventory = Inventory.objects.get(external_system_id=reference)
            serializer.validated_data['inventory'] = inventory.id

        instance = serializer.save(
            created_by=self.request.user,
            
            status=serializer.validated_data.get('status', StockItem.StockStatus.OK),
            
            batch=serializer.validated_data.get('batch') or generate_batch_code(),
            
        )

        # Handle serial number generation
        if not instance.serial:
            instance.serial = generate_serial_number(instance.part)
            instance.save()

        # Update parent stock (if specified)
        if instance.parent:
            instance.parent.update_quantity()