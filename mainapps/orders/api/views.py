from django.forms import ValidationError
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from mainapps.inventory.models import TransactionType
from mainapps.management.models_activity.changes import get_field_changes
from mainapps.permit.models import CombinedPermissions
from mainapps.permit.permit import HasModelRequestPermission
from middleware import permissions
from reports.emails.emails import send_purchase_order_email, send_return_order_email
from reports.emails.utils import generate_purchase_order_pdf, generate_return_order_pdf
from ..models import PurchaseOrder, PurchaseOrderLineItem, PurchaseOrderStatus, ReturnOrder, ReturnOrderLineItem, ReturnOrderStatus
from .serializers import PurchaseOrderLineItemSerializer, PurchaseOrderSerializer
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from mainapps.management.models_activity.activity_logger import log_user_activity
from rest_framework import viewsets
from django.db import transaction
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import status


class PurchaseOrderRetrieveView(generics.RetrieveAPIView):
    queryset = PurchaseOrder.objects.all()
    serializer_class = PurchaseOrderSerializer
    lookup_field = 'id' 
    permission_classes = [IsAuthenticated, HasModelRequestPermission]
    required_permission= CombinedPermissions.READ_PURCHASE_ORDER

    

class PurchaseOrderCreateView(generics.CreateAPIView):
    serializer_class = PurchaseOrderSerializer
    permission_classes = [IsAuthenticated, HasModelRequestPermission]
    required_permission= CombinedPermissions.CREATE_PURCHASE_ORDER

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        instance = serializer.instance
        log_user_activity(
            user=request.user,
            action='CREATE',
            instance=instance,
            details={
                'initial_data': request.data,
                'created_data': serializer.data,
                'ip_address': request.META.get('REMOTE_ADDR'),
                'user_agent': request.META.get('HTTP_USER_AGENT')
            },
            async_log=True
        )

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    

    def perform_create(self, serializer):
        user = self.request.user


        serializer.save(
            created_by=user, 
            profile=user.profile

        )


class PurchaseOrderUpdateView(APIView):
    
    permission_classes = [IsAuthenticated, HasModelRequestPermission]
    required_permission= CombinedPermissions.UPDATE_PURCHASE_ORDER

    def patch(self, request, pk, format=None):
        
        purchase_order = get_object_or_404(PurchaseOrder, pk=pk)
        original_data = PurchaseOrderSerializer(purchase_order).data
        

        serializer = PurchaseOrderSerializer(purchase_order, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            instance = serializer.instance
            log_user_activity(
            user=request.user,
            action='UPDATE',
            instance=instance,
            details={
                'changes': get_field_changes(original_data, serializer.data),
                'ip_address': request.META.get('REMOTE_ADDR'),
                'user_agent': request.META.get('HTTP_USER_AGENT')
            },
            async_log=True
        )
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PurchaseOrderDetailAPIView(generics.RetrieveAPIView):
    queryset = PurchaseOrder.objects.all()
    serializer_class = PurchaseOrderSerializer
    permission_classes = [IsAuthenticated, HasModelRequestPermission]
    required_permission= CombinedPermissions.READ_PURCHASE_ORDER
    lookup_field='reference'


class PurchaseOrderListCreateView(generics.ListAPIView):

    queryset = PurchaseOrder.objects.all()
    serializer_class = PurchaseOrderSerializer
    permission_classes = [IsAuthenticated, HasModelRequestPermission]
    required_permission= CombinedPermissions.READ_PURCHASE_ORDER

    def get_queryset(self):
        return super().get_queryset().filter(profile=self.request.user.profile)


class PurchaseOrderLineItemCreateView(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, HasModelRequestPermission]
    queryset = PurchaseOrderLineItem.objects.all()
    serializer_class = PurchaseOrderLineItemSerializer
    required_permission= {
        'create': CombinedPermissions.CREATE_PURCHASE_ORDER_LINE_ITEM,
        'update': CombinedPermissions.UPDATE_PURCHASE_ORDER_LINE_ITEM,
        'retrieve': CombinedPermissions.READ_PURCHASE_ORDER_LINE_ITEM,
        'destroy': CombinedPermissions.DELETE_PURCHASE_ORDER_LINE_ITEM,
        'list': CombinedPermissions.READ_PURCHASE_ORDER_LINE_ITEM,
    }
    def get_queryset(self):
        queryset = super().get_queryset()
        reference = self.request.query_params.get('reference')
        if reference:
            queryset = queryset.filter(purchase_order__reference=reference)
        return queryset
    def create(self, request, *args, **kwargs):
        reference=request.data.pop('purchase_order', None)
        try:
            if reference:
                purchase_order = PurchaseOrder.objects.get(reference=reference)
                request.data['purchase_order'] = purchase_order.id
            else:
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


class ApprovePurchaseOrderView(APIView):
    permission_classes = [IsAuthenticated,HasModelRequestPermission]
    required_permission= CombinedPermissions.APPROVE_PURCHASE_ORDER
    

    def put(self, request, pk):
        try:
            po = PurchaseOrder.objects.get(pk=pk)
        except PurchaseOrder.DoesNotExist:
            return Response({"error": "Purchase Order not found."}, status=status.HTTP_404_NOT_FOUND)

        if po.status != PurchaseOrderStatus.PENDING:
            return Response({"error": "Only draft orders can be approved."}, status=status.HTTP_400_BAD_REQUEST)

        po.status = PurchaseOrderStatus.APPROVED
        po.save()
        return Response({"message": "Purchase Order approved.", "status": po.status}, status=status.HTTP_200_OK)


class IssuePurchaseOrderView(APIView):
    permission_classes = [IsAuthenticated,HasModelRequestPermission] 
    required_permission= CombinedPermissions.ISSUE_PURCHASE_ORDER
        
    def put(self, request, pk):
            try:
                po = PurchaseOrder.objects.select_related('supplier', 'contact').prefetch_related('line_items').get(pk=pk)
            except PurchaseOrder.DoesNotExist:
                return Response({"error": "Purchase Order not found."}, status=status.HTTP_404_NOT_FOUND)

            po.total_price=sum(line_item.total_price for line_item in po.line_items.all())  
         
            print(po.total_price) 
            po.status = PurchaseOrderStatus.ISSUED
            po.issue_date = timezone.now()
            po.save()

            # Generate PDF
            pdf = generate_purchase_order_pdf(po)

            send_purchase_order_email(po, pdf)
          
            return Response({"message": "Purchase Order issued and email sent.", "status": po.status}, status=status.HTTP_200_OK)

class ReceivePurchaseOrderView(APIView):
    permission_classes = [IsAuthenticated,HasModelRequestPermission] 
    required_permission= CombinedPermissions.RECEIVE_PURCHASE_ORDER
        
    def put(self, request, pk):
            try:
                po = PurchaseOrder.objects.get(pk=pk)
                if not po.status == PurchaseOrderStatus.ISSUED:
                    return Response({"error": "Only issued orders can be received."}, status=status.HTTP_400_BAD_REQUEST)
            except PurchaseOrder.DoesNotExist:
                return Response({"error": "Purchase Order not found."}, status=status.HTTP_404_NOT_FOUND)

            
            po.status = PurchaseOrderStatus.RECEIVED
            po.received_date = timezone.now()
            po.received_by=request.user
            po.save()

            return Response({"message": "Purchase Order issued and email sent.", "status": po.status}, status=status.HTTP_200_OK)


class MarkPurchaseOrderCompleteView(APIView):
    permission_classes = [IsAuthenticated, HasModelRequestPermission]
    required_permission = CombinedPermissions.APPROVE_PURCHASE_ORDER
    

    def put(self, request, pk):
        try:
            # Get purchase order with related data
            po = PurchaseOrder.objects.get(pk=pk)
        except PurchaseOrder.DoesNotExist:
            return Response({"error": "Purchase Order not found."}, 
                          status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            print(e)
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Validate order status transition
        if po.status != PurchaseOrderStatus.RECEIVED:
            return Response(
                {
                "error": "Only received orders can be marked as complete."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            with transaction.atomic():
                po.status = PurchaseOrderStatus.COMPLETED
                po.complete_date = timezone.now()
                po.save()

                # Process line items and finalize stock updates
                for line_item in po.line_items.all():
                    if line_item.stock_item:
                        # Verify received quantity matches ordered quantity
                        
                        
                        # Update stock quantity with quality-checked items
                        line_item.stock_item.quantity += line_item.quantity
                        line_item.stock_item.save()
                    
                    line_item.save()

                # Create inventory transactions
                self.create_inventory_transactions(po)

        except ValidationError as e:
            print('error',e)
            return Response({"error": str(e)},
                          status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": f"Error completing order: {str(e)}"},
                          status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({
            "message": "Purchase Order completed and stock finalized.",
            "status": po.status
        }, status=status.HTTP_200_OK)

    def create_inventory_transactions(self, po):
        """Create audit records for inventory changes"""
        from mainapps.inventory.models import InventoryTransaction
        
        transactions = []
        for line_item in po.line_items.all():
            transactions.append(
                InventoryTransaction(
                    item=line_item.stock_item,
                    quantity=line_item.quantity,
                    unit_price=line_item.unit_price,
                    transaction_type=TransactionType.PO_COMPLETE,
                    reference=po.reference,
                    user=self.request.user,
                    profile=self.request.user.profile,
                    notes=f"Completed from PO {po.reference}"
                )
            )
        InventoryTransaction.objects.bulk_create(transactions)



class CreateReturnOrderView(APIView):
    permission_classes = [IsAuthenticated, HasModelRequestPermission]
    required_permission = CombinedPermissions.CREATE_RETURN_ORDER

    def post(self, request, po_id):
        try:
            po = PurchaseOrder.objects.get(pk=po_id)
        except PurchaseOrder.DoesNotExist:
            return Response({"error": "Purchase order not found"}, status=status.HTTP_404_NOT_FOUND)

        return_items = request.data.get('return_items', [])
        
        try:
            with transaction.atomic():
                # Create return order
                return_order = ReturnOrder.objects.create(
                    purchase_order=po,
                    profile=po.profile,
                    contact=po.contact,
                    address=po.address,
                    status=ReturnOrderStatus.PENDING,
                    created_by=request.user,
                    responsible=request.user
                )
                
                # Create line items
                for item in return_items:
                    line_item = po.line_items.get(id=item['line_item_id'])
                    
                    ReturnOrderLineItem.objects.create(
                        return_order=return_order,
                        original_line_item=line_item,
                        quantity_returned=item['quantity'],
                        unit_price=line_item.unit_price,
                        tax_rate=line_item.tax_rate,
                        discount=line_item.discount,
                        return_reason=item.get('reason', '')
                    )
                
                # Generate PDFs
                po_pdf = generate_purchase_order_pdf(po)
                return_pdf = generate_return_order_pdf(return_order)
                
                # Send email notification
                send_return_order_email(
                    return_order,
                    po_pdf=po_pdf,
                    return_pdf=return_pdf
                )
                
                return Response({
                    "message": "Return order created successfully",
                    "return_order": return_order.reference
                }, status=status.HTTP_201_CREATED)
                
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)