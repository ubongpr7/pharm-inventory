"""Stock database model definitions."""

from __future__ import annotations


from django.core.validators import MinValueValidator
from django.db import models, transaction
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from mptt.models import MPTTModel, TreeForeignKey
from django.utils.text import slugify
from django.utils.crypto import get_random_string


from mainapps.common.custom_fields import MoneyField
from mainapps.common.models import AttributeStore, User
from mainapps.company.models import Company
from mainapps.inventory.models import InventoryMixin 
from mainapps.orders.models import *
from django.utils.crypto import get_random_string

from django.utils.text import slugify
# from mainapps.utils.statuses import StockStatus
from mainapps.utils.generators import generate_batch_code
from mainapps.utils.validators import validate_batch_code, validate_serial_number



class StockStatus(models.IntegerChoices):
    """
    Integer choices for stock item status with additional metadata.
    Inherits from IntegerChoices for Django integration.
    """
    
    OK = 10, _('OK')
    ATTENTION = 50, _('Attention needed')
    DAMAGED = 55, _('Damaged')
    DESTROYED = 60, _('Destroyed')
    REJECTED = 65, _('Rejected')
    LOST = 70, _('Lost')
    QUARANTINED = 75, _('Quarantined')
    RETURNED = 85, _('Returned')

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

    def __str__(self):
        return self.name


class StockLocation(InventoryMixin,MPTTModel):
    
    """
    Represents an organizational tree for StockItem objects.

    A "StockLocation" can be considered a warehouse or storage location.
    Stock locations can be hierarchical as required.

    Attributes:
        - manager (User): User who manages the stock location (optional).
        - structural (bool): Indicates if stock items can be directly located into this stock location.
        - external (bool): Indicates if this is an external stock location.
        - location_type (StockLocationType): The type of the stock location.
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
        constraints = [
            models.UniqueConstraint(
                fields=['inventory', 'name'],
                name='unique_location_name_per_inventory'
            )
        ]

    @classmethod
    def get_verbose_names(self,p=None):
        if str(p) =='0':
            return "Stock Location"
        return "Stock Locations "
    @property
    def get_label(self):
        return 'stocklocation'
    @classmethod
    def return_numbers(self,profile) :
        return self.objects.filter(inventory__profile=profile).count()

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

    def __str__(self):
        return f"{self.name} ({self.location_type.name})" if self.location_type else self.name
    
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
        - build: Link to a Build (if this stock item was created from a build)
        - is_building: Boolean field indicating if this stock item is currently being built (or is "in production")
        - purchase_order: Link to a PurchaseOrder (if this stock item was created from a PurchaseOrder)
        - sales_order: Link to a SalesOrder object (if the StockItem has been assigned to a SalesOrder)
        - purchase_price: The unit purchase price for this StockItem - this is the unit price at the time of purchase 
          (if this item was purchased from an external supplier)
        - packaging: Description of how the StockItem is packaged (e.g. "reel", "loose", "tape" etc)
    """

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
        max_length=50,
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
        validators=[validate_serial_number],
    )
    
    sku = models.CharField(
        verbose_name=_('Stock keeping unit'),
        max_length=100,
        blank=True,
        null=True,
        help_text=_('Stock keeping unit for this stock item'),
        validators=[validate_serial_number],
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
        default=generate_batch_code,
        validators=[validate_batch_code],
    )

    quantity = models.DecimalField(
        verbose_name=_('Stock Quantity'),
        max_digits=15,
        decimal_places=5,
        validators=[MinValueValidator(0)],
        default=1,
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

    status = models.PositiveIntegerField(
        default=StockStatus.OK,
        choices=StockStatus.choices,
        validators=[MinValueValidator(0)],
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
    

    @property
    def status_text(self):
        """Return the text representation of the status field."""
        return StockStatus.text(self.status)

    def get_absolute_url(self):
        """Return the absolute URL for the StockItem detail view."""
        return reverse('stock-item-detail', args=[str(self.pk)])

    def __str__(self):
        """Return a string representation of the StockItem."""
        return f"{self.serial or ''} - {self.quantity} {self.part.unit}"

    class Meta:
        verbose_name = _('Stock Item')
        verbose_name_plural = _('Stock Items')
    @classmethod
    def get_verbose_names(self,p=None):
        if str(p) =='0':
            return "Stock Item"
        return "Stock Items"
    @property
    def get_label(self):
        return 'stockitem'
    @classmethod
    def return_numbers(self,profile) :
        return self.objects.filter(inventory__profile=profile).count()


class StockItemTracking(InventoryMixin):
    """Stock tracking entry - used for tracking history of a particular StockItem.


    Attributes:
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
