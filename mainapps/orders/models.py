
import logging
import os
import sys
from datetime import datetime
from decimal import Decimal
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import IntegrityError, models, transaction
from django.db.models import F, Q
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.fields import GenericForeignKey,GenericRelation

from mainapps.management.models import CompanyProfile
from mptt.models import TreeForeignKey

from django.utils import timezone
from mainapps.company.models import  Company, CompanyAddress, Contact 
from mainapps.common.models  import Currency, User
from mainapps.content_type_linking_models.models import Attachment
from mainapps.inventory.helpers.field_validators import validate_currency_code
from mainapps.inventory.models import InventoryMixin 
from mainapps.utils.statuses import *

class PurchaseOrderLineItem(models.Model):
    purchase_order = models.ForeignKey('PurchaseOrder', on_delete=models.CASCADE, related_name='line_items')
    stock_item = models.ForeignKey('stock.StockItem', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, editable=False)

    def save(self, *args, **kwargs):
        self.total_price = self.quantity * self.unit_price
        super().save(*args, **kwargs)

class TotalPriceMixin(models.Model):
    """Mixin which provides 'total_price' field for an order."""

    class Meta:
        """Meta for MetadataMixin."""

        abstract = True

    
    total_price = models.PositiveBigIntegerField(
        null=True,
        blank=True,
        verbose_name=_('Total Price'),
        help_text=_('Total price for this order'),
    )

    order_currency =models.ForeignKey(
        Currency,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

class Order(InventoryMixin):
    """
    Abstract model for an order.

    Instances of this class:

    - PurchaseOrder
    - SalesOrder

    Attributes:
        reference: Unique order number / reference / code
        description: Long-form description (required)
        notes: Extra note field (optional)
        creation_date: Automatic date of order creation
        created_by: User who created this order (automatically captured)
        issue_date: Date the order was issued
        complete_date: Date the order was completed
        responsible: User (or group) responsible for managing the order
    """

    class Meta:
        """
        Metaclass options. Abstract ensures no database table is created.
        """
        abstract = True

    description = models.CharField(
        max_length=250,
        blank=True,
        verbose_name=_('Description'),
        help_text=_('Order description (optional)'),
    )


    link = models.URLField(
        blank=True, verbose_name=_('Link'), help_text=_('Link to an external page')
    )

    delivery_date = models.DateField(
        blank=True,
        null=True,
        verbose_name=_('Delivery Date'),
        help_text=_(
            'Expected date for order delivery. Order will be overdue after this date.'
        ),
    )

    
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='+',
        verbose_name=_('Created By'),
    )

    responsible = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        help_text=_('User or group responsible for this order'),
        verbose_name=_('Responsible'),
        related_name='+',
    )

    contact = models.ForeignKey(
        Contact,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name=_('Contact Person'),
        help_text=_('Point of contact for this order, that is the person you should keep in contact with for this order in the affiliated business'),
        related_name='+',
    )

    address = models.ForeignKey(
        CompanyAddress,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name=_('Address'),
        help_text=_('Company address for this order of the affiliated business'),
        related_name='+',
    )
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    
    def generate_reference(self, prefix):
        """Atomically generate unique PO reference in PREFIX-YYYYMMDD-SEQ format"""
        with transaction.atomic():
            profile = CompanyProfile.objects.select_for_update().get(pk=self.inventory.profile.pk)
            
            date_str = timezone.now().strftime("%Y%m%d")
            
            sequence_number = profile.po_sequence + 1  # Add 'po_sequence' field to CompanyProfile
            profile.po_sequence = F('po_sequence') + 1
            profile.save(update_fields=['po_sequence'])
            
            # Refresh to get updated value
            profile.refresh_from_db()
            
            # Build reference components
            components = [
                prefix.upper(),
                date_str,
                f"{self.inventory.id:03d}", 
                f"{profile.po_sequence:04d}"
            ]
            
            return '-'.join(components)

class PurchaseOrder(TotalPriceMixin, Order):
    """A PurchaseOrder represents goods shipped inwards from an external supplier.

    Attributes:
        supplier: Reference to the company supplying the goods in the order
        supplier_reference: Optional field for supplier order reference code
        received_by: User that received the goods
        target_date: Expected delivery target date for PurchaseOrder completion (optional)
    """

    reference = models.CharField(
        unique=True,
        max_length=64,
        verbose_name=_('Reference'),
        help_text=_('Order reference'),
        editable=False,
    )

    status = models.PositiveIntegerField(
        default=PurchaseOrderStatus.PENDING.value,
        choices=PurchaseOrderStatus.items(),
        help_text=_('Purchase order status'),
    )

    supplier = models.ForeignKey(
        Company,
        on_delete=models.SET_NULL,
        null=True,
        limit_choices_to={'is_supplier': True},
        related_name='+',
        verbose_name=_('Supplier'),
        help_text=_('Company from which the items are being ordered'),
    )

    supplier_reference = models.CharField(
        max_length=64,
        blank=True,
        null=True,
        verbose_name=_('Supplier Reference'),
        help_text=_('Supplier order reference code'),
    )

    received_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='received_purchase_orders',
        verbose_name=_('Received by'),
    )

    issue_date = models.DateField(
        blank=True,
        null=True,
        verbose_name=_('Issue Date'),
        help_text=_('Date order was issued'),
    )

    complete_date = models.DateField(
        blank=True,
        null=True,
        verbose_name=_('Completion Date'),
        help_text=_('Date order was completed'),
    )
    attachment= GenericRelation(Attachment,related_query_name='purchase_oders')

    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = self.generate_reference("PO")
        super().save(*args, **kwargs)

class SalesOrder(TotalPriceMixin, Order):
    """A SalesOrder represents a list of goods shipped outwards to a customer."""

    
    customer_reference = models.CharField(
        max_length=64,
        blank=True,
        verbose_name=_('Customer Reference '),
        help_text=_('Customer order reference code'),
    )

    shipment_date = models.DateField(
        blank=True, null=True, verbose_name=_('Shipment Date')
    )

    shipped_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='shipped_sales',
        verbose_name=_('shipped by'),
    )
    attachment= GenericRelation(Attachment,related_query_name='sales_oders')



class SalesOrderShipment(InventoryMixin):
    """The SalesOrderShipment model represents a physical shipment made against a SalesOrder.

    - Points to a single SalesOrder object
    - Multiple SalesOrderAllocation objects point to a particular SalesOrderShipment
    - When a given SalesOrderShipment is "shipped", stock items are removed from stock

    Attributes:
        order: SalesOrder reference
        shipment_date: Date this shipment was "shipped" (or null)
        checked_by: User reference field indicating who checked this order
        reference: Custom reference text for this shipment (e.g. consignment number?)
        notes: Custom notes field for this shipment
    """

    class Meta:
        """Metaclass defines extra model options."""

        # Shipment reference must be unique for a given sales order
        unique_together = ['order', 'reference']
   
    order = models.ForeignKey(
        SalesOrder,
        on_delete=models.CASCADE,
        blank=False,
        null=False,
        related_name='+',
        verbose_name=_('Order'),
        help_text=_('Sales Order'),
    )

    shipment_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_('Shipment Date'),
        help_text=_('Date of shipment'),
    )

    delivery_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_('Delivery Date'),
        help_text=_('Date of delivery of shipment'),
    )

    checked_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name=_('Checked By'),
        help_text=_('User who checked this shipment'),
        related_name='+',
    )

    reference = models.CharField(
        max_length=100,
        blank=False,
        verbose_name=_('Shipment'),
        help_text=_('Shipment number'),
        default='1',
    )

    tracking_number = models.CharField(
        max_length=100,
        blank=True,
        unique=False,
        verbose_name=_('Tracking Number'),
        help_text=_('Shipment tracking information'),
    )

    invoice_number = models.CharField(
        max_length=100,
        blank=True,
        unique=False,
        verbose_name=_('Invoice Number'),
        help_text=_('Reference number for associated invoice'),
    )

    link = models.URLField(
        blank=True, verbose_name=_('Link'), help_text=_('Link to external page')
    )


class ReturnOrder(TotalPriceMixin, Order):
    """A ReturnOrder represents goods returned from a customer, e.g. an RMA or warranty.

    Attributes:
        customer: Reference to the customer
        sales_order: Reference to an existing SalesOrder (optional)
        status: The status of the order (refer to statuses.ReturnOrderStatus)
        attachment: (Attachment) attached files
    """
    reference = models.CharField(
        unique=True,
        max_length=64,
        blank=False,
        verbose_name=_('Reference'),
        help_text=_('Return Order reference'),
        # default=order.validators.generate_next_return_order_reference,
        # validators=[order.validators.validate_return_order_reference],
    )

    customer = models.ForeignKey(
        'company.Company',
        on_delete=models.SET_NULL,
        null=True,
        limit_choices_to={'is_customer': True},
        related_name='+',
        verbose_name=_('Customer'),
        help_text=_('Company from which items are being returned'),
    )


    status = models.PositiveIntegerField(
        default=ReturnOrderStatus.PENDING.value,
        choices=ReturnOrderStatus.items(),
        verbose_name=_('Status'),
        help_text=_('Return order status'),
    )

    customer_reference = models.CharField(
        max_length=64,
        blank=True,
        verbose_name=_('Customer Reference '),
        help_text=_('Customer order reference code'),
    )

    issue_date = models.DateField(
        blank=True,
        null=True,
        verbose_name=_('Issue Date'),
        help_text=_('Date order was issued'),
    )

    complete_date = models.DateField(
        blank=True,
        null=True,
        verbose_name=_('Completion Date'),
        help_text=_('Date order was completed'),
    )
    attachment= GenericRelation(Attachment,related_query_name='return_oders')
   
    

registerable_models=[
    ReturnOrder,
    PurchaseOrder,
    SalesOrderShipment,
    SalesOrder,

    ]

