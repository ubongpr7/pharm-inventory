"""Stock database model definitions."""

from __future__ import annotations


from django.core.validators import MinValueValidator
from django.db import models

class Stock(models.Model):
    """
    Represents a stock item in the pharmaceutical inventory system.
    
    Attributes:
        product (ForeignKey): Reference to the Product model
        batch_number (str): Unique identifier for the product batch
        quantity (int): Current stock quantity
        expiry_date (Date): Expiration date of the batch
        location (str): Storage location in warehouse
        last_updated (DateTime): Timestamp of last stock update
    """
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from mptt.models import MPTTModel, TreeForeignKey
from django.utils.text import slugify
from django.utils.crypto import get_random_string

from  django.utils import timezone
from mainapps.common.custom_fields import MoneyField
from mainapps.common.models import AttributeStore, User
from mainapps.company.models import Company
from mainapps.inventory.models import InventoryMixin 
from mainapps.orders.models import *
from django.utils.crypto import get_random_string

from django.utils.text import slugify
from mainapps.utils.generators import generate_batch_code
from mainapps.utils.validators import validate_batch_code, validate_serial_number



class StockStatus(models.TextChoices):
    """
    Integer choices for stock item status with additional metadata.
    Inherits from IntegerChoices for Django integration.
    """
    
    OK = 'ok', _('OK')
    ATTENTION = 'attention_needed', _('Attention needed')
    DAMAGED = 'damaged', _('Damaged')
    DESTROYED = 'destroyed', _('Destroyed')
    REJECTED = 'rejected', _('Rejected')
    LOST = 'lost', _('Lost')
    QUARANTINED = 'quarantined', _('Quarantined')
    RETURNED = 'returned', _('Returned')

class TrackingType(models.IntegerChoices):
    """
    Types of stock tracking events with additional metadata
    """
    # Inbound Operations
    RECEIVED = 10, _('Items received from supplier')
    PURCHASE_ORDER_RECEIPT = 11, _('Received against purchase order')
    RETURNED_FROM_CUSTOMER = 12, _('Items returned from customer')
    
    # Outbound Operations
    SHIPPED = 20, _('Items shipped to customer')
    SALES_ORDER_SHIPMENT = 21, _('Shipped against sales order')
    CONSUMED_IN_BUILD = 22, _('Used in manufacturing process')
    
    # Internal Operations
    STOCK_ADJUSTMENT = 30, _('Manual quantity adjustment')
    LOCATION_CHANGE = 31, _('Moved between locations')
    SPLIT_FROM_PARENT = 32, _('Split from parent stock')
    MERGED_WITH_PARENT = 33, _('Merged with parent stock')
    
    # Quality Operations
    QUARANTINED = 40, _('Placed in quarantine')
    QUALITY_CHECK = 41, _('Quality inspection performed')
    REJECTED = 42, _('Rejected during inspection')
    
    # System Events
    STOCKTAKE = 50, _('Manual stock count performed')
    AUTO_RESTOCK = 51, _('Automatic restock triggered')
    EXPIRY_WARNING = 52, _('Near expiry date notification')
    
    # Status Changes
    STATUS_CHANGE = 60, _('Stock status updated')
    DAMAGE_REPORTED = 61, _('Damage reported on item')
    
    # Default/Unknown
    OTHER = 0, _('Other Uncategorized tracking event')


class StockLocationType(models.Model):
    """
    A type of stock location like Warehouse, room, shelf, drawer.

    Attributes:
        - name (str): Brief name for the stock location type (unique).
        - description (str): Longer form description of the stock location type (optional).
    """

    name = models.CharField(
        unique=True,
        blank=False, 
        max_length=100, 
        verbose_name=_('Name'), 
        help_text=_('Brief name for the stock location type (unique)'),
    )

    description = models.CharField(
        blank=True,
        max_length=250,
        verbose_name=_('Description'),
        help_text=_('Longer form description of the stock location type (optional)'),
    )


    class Meta:
        """Metaclass defines extra model properties."""
        verbose_name = _('Stock Location Type')
        verbose_name_plural = _('Stock Location Types')
        ordering = ['id']

    def __str__(self):
        return self.name


class StockLocation(MPTTModel):
    """
    Represents an organizational tree for StockItem objects (warehouse/storage locations).
    
    Key Attributes:
        code: Auto-generated unique location identifier
        name: Human-readable location name  
        parent: Parent location in hierarchy
        location_type: Classification of location type
        structural: If location can directly contain stock items
        external: If location is outside main warehouse
        description: Additional location details
        
    Methods:
        save(): Auto-generates location code on first save
        __str__(): Returns formatted location identifier
    """

    ITEM_PARENT_KEY = 'location'

    class Meta:
        """
        Metaclass defines extra model properties.

        Attributes:
            - verbose_name (str): Singular name for the model.
            - verbose_name_plural (str): Plural name for the model.
        """
        verbose_name = _('Stock Location')
        verbose_name_plural = _('Stock Locations')
    code = models.CharField(
        max_length=100,
        unique=True,
        editable=False,
        null=True,
        blank=True,
        verbose_name=_('Location Code'),
        help_text=_('Unique location identifier (auto-generated)')
    ) 
    profile=models.ForeignKey(
        CompanyProfile,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='stock_locations',
        verbose_name=_('Profile'),
        help_text=_('Profile for this stock location'),
    )
    
    name=models.CharField(max_length=200, null=True, blank=False)
    official = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name=_('Manager'),
        help_text=_('Select the manager for this stock location'),
        related_name='stock_locations',
    )

    structural = models.BooleanField(
        default=False,
        verbose_name=_('Structural'),
        help_text=_(
            'Stock items may not be directly located into a structural stock location, '
            'but may be located to child locations.'
        ),
    )
    
    parent = TreeForeignKey(
        'self',
        null=True,
        blank=True,
        related_name='children',
        on_delete=models.CASCADE,
        verbose_name=_('Super Location'),
        help_text=_('The location this falls under eg if this is a sub location in a bigger location like warehouse'),
    )

    external = models.BooleanField(
        default=False,
        verbose_name=_('External'),
        help_text=_('This is an external stock location'),
    )

    location_type = models.ForeignKey(
        StockLocationType,
        on_delete=models.SET_NULL,
        verbose_name=_('Location type'),
        related_name='stock_locations',
        null=True,
        blank=True,
        help_text=_('Stock location type of this location'),
    )

    description = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Description'),
        help_text=_('Longer form description of the stock location (optional)'),
    )
    created_at = models.DateTimeField(
        default=timezone.now,
        verbose_name=_('Created at'),
        help_text=_('Date that this stock location was created'),
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Updated at'),
        help_text=_('Date that this stock location was last updated'),
    )
    def __str__(self):
        return f"{self.name}- {self.code} ({self.location_type.name})" if self.location_type else self.name
    def save(self, *args, **kwargs):
        """Auto-generate location code on first save"""
        if not self.pk and self.location_type and self.profile:
            base = self.location_type.name.upper().replace(' ', '_')
            profile_id = self.profile.id
            
            # Get highest existing sequence number for this type+profile combination
            last_code = StockLocation.objects.filter(
                location_type=self.location_type,
                profile=self.profile,
                code__startswith=f"{base}_{profile_id}_"
            ).order_by('-code').values_list('code', flat=True).first()

            sequence = 1
            if last_code:
                try:
                    sequence = int(last_code.split('_')[-1]) + 1
                except (ValueError, IndexError):
                    pass

            self.code = f"{base}_{profile_id}_{sequence:03d}"

        super().save(*args, **kwargs)
    
class StockItem(MPTTModel, InventoryMixin):
    """
    A StockItem object represents a quantity of physical instances of a part.

    Attributes:
        - parent: Link to another StockItem from which this StockItem was created
        - location: Where this StockItem is located
        - quantity: Number of stocked units
        - batch: Batch number for this StockItem
        - serial: Unique serial number for this StockItem
        - link: Optional URL to link to an external resource
        - updated: Date that this stock item was last updated (auto)
        - expiry_date: Expiry date of the StockItem (optional)
        - stocktake_date: Date of the last stocktake for this item
        - stocktaker: User that performed the most recent stocktake
        - review_needed: Flag if StockItem needs review
        - delete_on_deplete: If True, StockItem will be deleted when the stock level gets to zero
        - status: Status of this StockItem 
        - notes: Extra notes field
        - purchase_order: Link to a PurchaseOrder (if this stock item was created from a PurchaseOrder)
        - sales_order: Link to a SalesOrder object (if the StockItem has been assigned to a SalesOrder)
        - purchase_price: The unit purchase price for this StockItem - this is the unit price at the time of purchase 
          (if this item was purchased from an external supplier)
        - packaging: Description of how the StockItem is packaged (e.g. "reel", "loose", "tape" etc)
    """
    
    
    variant = models.ForeignKey(
        'product.ProductVariant',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='stock_items',
        help_text=_('Product variant'),
        verbose_name=_('Product Variant'),
    )

    name=models.CharField(
        max_length=200,
        null=True,
        blank=False,
        verbose_name=_('Name'),
        help_text=_('Name of the stock item'),
    )
    parent = TreeForeignKey(
        'self',
        verbose_name=_('Parent Stock Item'),
        on_delete=models.DO_NOTHING,
        blank=True,
        null=True,
        related_name='children',
        help_text=_('Link to another StockItem from which this StockItem was created'),
    )
    location = TreeForeignKey(
        StockLocation,
        on_delete=models.DO_NOTHING,
        verbose_name=_('Stock Location'),
        related_name='stock_items',
        blank=True,
        null=True,
        help_text=_('Where this StockItem is located'),
    )

    packaging = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_('Packaging'),
        help_text=_('Description of how the StockItem is packaged (e.g. "reel", "loose", "tape" etc)'),
    )
    belongs_to = models.ForeignKey(
        'self',
        verbose_name=_('Installed In'),
        on_delete=models.CASCADE,
        related_name='installed_parts',
        blank=True,
        null=True,
        help_text=_('Is this item installed in another item?'),
    )

    customer = models.ForeignKey(
        Company,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={'is_customer': True},
        related_name='assigned_stock',
        help_text=_('Customer'),
        verbose_name=_('Customer'),
    )

    serial = models.CharField(
        verbose_name=_('Serial Number'),
        max_length=100,
        blank=True,
        null=True,
        help_text=_('Unique serial number for this StockItem'),
    )
    
    sku = models.CharField(
        verbose_name=_('Stock keeping unit'),
        max_length=100,
        blank=True,
        null=True,
        help_text=_('Stock keeping unit for this stock item'),
    )
    serial_int = models.IntegerField(default=0)
    
    link = models.URLField(
        verbose_name=_('External Link'),
        blank=True,
        null=True,
        help_text=_('Optional URL to link to an external resource'),
    )

    batch = models.CharField(
        verbose_name=_('Batch Code'),
        max_length=100,
        blank=True,
        null=True,
        help_text=_('Batch code for this stock item'),
    )

    quantity = models.DecimalField(
        verbose_name=_('Stock Quantity'),
        max_digits=15,
        decimal_places=5,
        validators=[MinValueValidator(Decimal('0'))],  
        default=Decimal('1'),
    )

    purchase_order = models.ForeignKey(
        PurchaseOrder,
        on_delete=models.SET_NULL,
        verbose_name=_('Source Purchase Order'),
        related_name='stock_items',
        blank=True,
        null=True,
        help_text=_('Link to a PurchaseOrder (if this stock item was created from a PurchaseOrder)'),
    )

    sales_order = models.ForeignKey(
        SalesOrder,
        on_delete=models.SET_NULL,
        verbose_name=_('Destination Sales Order'),
        related_name='stock_items',
        null=True,
        blank=True,
        help_text=_("Link   item to a SalesOrder")
    )

    expiry_date = models.DateField(
        blank=True,
        null=True,
        verbose_name=_('Expiry Date'),
        help_text=_('Expiry date for stock item. Stock will be considered expired after this date'),
    )

    stocktake_date = models.DateField(blank=True, null=True)

    stocktaker = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='stocktakes',
        help_text=_('User that performed the most recent stocktake'),
    )

    review_needed = models.BooleanField(default=False)

    delete_on_deplete = models.BooleanField(
        default=False,
        verbose_name=_('Delete on deplete'),
        help_text=_('Delete this Stock Item when stock is depleted'),
    )

    status = models.CharField(
        default=StockStatus.OK,
        choices=StockStatus.choices,
        max_length=50,
        verbose_name=_('Status'),
        help_text=_('Status of this StockItem '),
    )

    purchase_price = MoneyField(
        max_digits=30,
        decimal_places=7,
        blank=True,
        null=True,
        verbose_name=_('Purchase Price'),
        help_text=_('Single unit purchase price at the time of purchase'),
    )
    
    notes= models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Notes'),
        help_text=_('Extra notes field'),
    )
    def __str__(self):
        """Return a string representation of the StockItem."""
        return f"{self.name} {self.serial or ''} - {self.quantity}"
    def save(self, *args, **kwargs):
        if not self.sku:
            company_id = self.inventory.profile.id
            inv_id = self.inventory.id
            inv_type = self.inventory.inventory_type.name[:4].upper()
            category_code = self.inventory.category.name[:5].upper()

            count = StockItem.objects.filter(inventory=self.inventory).count() + 1
            self.sku = f"C{company_id}-{inv_type}-{category_code}-{inv_id:05d}-{count:05d}"
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = _('Stock Item')
        verbose_name_plural = _('Stock Items')
        ordering = ['name','serial']
        indexes = [
            models.Index(fields=['variant']),  
            models.Index(fields=['location']),
            models.Index(fields=['batch', 'serial']),
        ]
    


class StockPricing(models.Model):
    """
    Tracks pricing information and discounts for stock items.
    
    Key Attributes:
        stock_item: Related stock item
        selling_price: Current selling price
        discount_flat: Fixed amount discount
        discount_rate: Percentage discount
        tax_rate: Applicable tax rate
        price_effective_from: When price takes effect
        price_effective_to: When price expires
        
    Methods:
        get_discount_amount(): Calculates total discount
        get_tax_amount(): Calculates tax after discount
        get_total_price(): Calculates final price
    """
    stock_item = models.ForeignKey(StockItem, on_delete=models.CASCADE,related_name='pricings')
    selling_price = models.DecimalField(max_digits=12, decimal_places=2)
    discount_flat = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    discount_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)  
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)  

    price_effective_from = models.DateTimeField(default=timezone.now)
    price_effective_to = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.stock_item.name} - ₦{self.selling_price}"

    def get_discount_amount(self):
        return (self.selling_price * self.discount_rate / 100) + self.discount_flat

    def get_tax_amount(self):
        price_after_discount = self.selling_price - self.get_discount_amount()
        return price_after_discount * self.tax_rate / 100

    def get_total_price(self):
        return self.selling_price - self.get_discount_amount() + self.get_tax_amount()

    
class StockItemTracking(InventoryMixin):
    """
    Tracks historical changes and movements of stock items.
    
    Key Attributes:
        item: Related stock item
        item: ForeignKey reference to a particular StockItem
        date: Date that this tracking info was created
        tracking_type: The type of tracking information
        notes: Associated notes (input by user)
        user: The user associated with this tracking info
        deltas: The changes associated with this history item
    """


    tracking_type = models.IntegerField(default=TrackingType.OTHER,choices=TrackingType.choices,)

    item = models.ForeignKey(
        StockItem, on_delete=models.CASCADE, related_name='tracking_info'
    )

    date = models.DateTimeField(auto_now_add=True, editable=False)

    notes = models.CharField(
        blank=True,
        null=True,
        max_length=512,
        verbose_name=_('Notes'),
        help_text=_('Entry notes'),
    )

    user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True,related_name='tracked_info')

    deltas = models.JSONField(null=True, blank=True)
    @classmethod
    def get_verbose_names(self,p=None):
        if str(p) =='0':
            return "Stock Tracking "
        return "Stock Tracking"
    @property
    def get_label(self):
        return 'stockitemtracking'
    @classmethod
    def return_numbers(self,profile) :
        return self.objects.filter(inventory__profile=profile).count()
    class Meta:
        indexes = [
            models.Index(fields=['date', 'item'])
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(tracking_type__in=TrackingType.values),
                name='valid_tracking_type'
            )
        ]

registerable_models=[StockLocationType,StockLocation,StockItemTracking,StockItem,]
