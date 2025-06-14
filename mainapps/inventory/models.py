import uuid
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.contrib.auth.models import Permission
from django.contrib.auth.models import Group
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.conf import settings
from mainapps.common.custom_fields import MoneyField
from mainapps.common.settings import DEFAULT_CURRENCY_CODE, currency_code_mappings
from mainapps.inventory.helpers.field_validators import validate_currency_code
from mptt.models import MPTTModel, TreeForeignKey
from django.utils.crypto import get_random_string
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from mainapps.common.models import Currency, TypeOf, User
from mainapps.content_type_linking_models.models import UUIDBaseModel
from mainapps.management.models import CompanyProfile
from django.db import models, transaction
from django.db.models import F


class RecallPolicies(models.TextChoices):
    REMOVE = "0", _("Remove from Stock")
    NOTIFY_CUSTOMERS = "1", _("Notify Customers")
    REPLACE_PRODUCT = "3", _("Replace Item")
    DESTROY = "4", _("Destroy Item")
    REPAIR = "5", _("Repair Item")
class ReorderStrategies(models.TextChoices):
    FIXED_QUANTITY = "FQ", _("Fixed Quantity")
    FIXED_INTERVAL = "FI", _("Fixed Interval")
    DYNAMIC = "DY", _("Demand-Based")
class ExpirePolicies(models.TextChoices):
    REMOVE = "0", _("Dispose of Stock")
    RETURN_MANUFACTURER = "1", _("Return to Manufacturer")
class NearExpiryActions(models.TextChoices):
    DISCOUNT = "DISCOUNT", _("Sell at Discount")
    DONATE = "DONATE", _("Donate to Charity")
    DESTROY = "DESTROY", _("Destroy Immediately")
    RETURN = "RETURN", _("Return to Supplier")

class ForecastMethods(models.TextChoices):
    SIMPLE_AVERAGE = "SA", _("Simple Average")
    MOVING_AVERAGE = "MA", _("Moving Average")
    EXP_SMOOTHING = "ES", _("Exponential Smoothing")


class InventoryPolicy(models.Model):
    """
    Central policy framework governing inventory operations.
    Defines rules for stock management, replenishment, and risk mitigation.
    
    Policies:
        - Stock replenishment rules and automation
        - Safety stock calculations
        - Expiration handling procedures
        - Recall management protocols
        - Cost optimization parameters
    """
    
    class Meta:
        abstract = True

    minimum_stock_level = models.IntegerField(
        _("Minimum Stock Level"),
        default=0,
        help_text=_("Trigger point for low stock alerts (units)")
    )
    
    re_order_point = models.IntegerField(
        _("Reorder Point"),
        default=10,
        help_text=_("Inventory level triggering replenishment (units)")
    )
    
    re_order_quantity = models.IntegerField(
        _("Reorder Quantity"),
        default=200,
        help_text=_("Standard quantity for automated replenishment")
    )
    
    automate_reorder = models.BooleanField(
        _("Auto-Replenish"),
        default=False,
        help_text=_("Enable automatic purchase orders at reorder point")
    )

    # Safety Stock Parameters
    safety_stock_level = models.IntegerField(
        _("Safety Stock"),
        default=0,
        help_text=_("Buffer stock for demand/supply fluctuations")
    )
    
    supplier_lead_time = models.IntegerField(
        _("Supplier Lead Time"),
        default=0,
        help_text=_("Average replenishment duration (days)")
    )
    
    internal_processing_time = models.IntegerField(
        _("Internal Processing Time"),
        default=1,
        help_text=_("Days needed for internal order processing")
    )

    # Replenishment Strategy

    reorder_strategy = models.CharField(
        _("Replenishment Strategy"),
        max_length=2,
        choices=ReorderStrategies.choices,
        default=ReorderStrategies.FIXED_QUANTITY,
        help_text=_("Methodology for inventory replenishment")
    )

    # Expiration Management
    expiration_threshold = models.IntegerField(
        _("Expiration Alert Window"),
        default=30,
        help_text=_("Days before expiry to trigger alerts")
    )
    
    batch_tracking_enabled = models.BooleanField(
        _("Batch Tracking"),
        default=False,
        help_text=_("Enable batch/lot number tracking for items")
    )

    # Cost Parameters
    holding_cost_per_unit = models.DecimalField(
        _("Holding Cost"),
        max_digits=10,
        decimal_places=2,
        default=0.0,
        help_text=_("Annual storage cost per unit")
    )
    
    ordering_cost = models.DecimalField(
        _("Ordering Cost"),
        max_digits=10,
        decimal_places=2,
        default=0.0,
        help_text=_("Fixed cost per replenishment order")
    )
    
    stockout_cost = models.DecimalField(
        _("Stockout Cost"),
        max_digits=10,
        decimal_places=2,
        default=0.0,
        help_text=_("Estimated cost per unit of stockout")
    )

    # Expiration Handling Policies

    expiration_policy = models.CharField(
        _("Expiration Handling"),
        max_length=200,
        choices=ExpirePolicies.choices,
        default=ExpirePolicies.REMOVE,
        help_text=_("Procedure for expired inventory items")
    )

    # Recall Management Policies

    recall_policy = models.CharField(
        _("Recall Procedure"),
        max_length=200,
        choices=RecallPolicies.choices,
        default=RecallPolicies.REMOVE,
        help_text=_("Protocol for product recall scenarios")
    )

    # Near-Expiry Actions

    near_expiry_policy = models.CharField(
        _("Near-Expiry Action"),
        max_length=20,
        choices=NearExpiryActions.choices,
        default=NearExpiryActions.DISCOUNT,
        help_text=_("Action plan for items nearing expiration")
    )

    # Demand Forecasting

    forecast_method = models.CharField(
        _("Forecast Method"),
        max_length=2,
        choices=ForecastMethods.choices,
        default=ForecastMethods.SIMPLE_AVERAGE,
        help_text=_("Algorithm for demand prediction")
    )

    # Supplier Management
    supplier_reliability_score = models.DecimalField(
        _("Supplier Score"),
        max_digits=5,
        decimal_places=2,
        default=100.0,
        help_text=_("Performance rating (0-100 scale)")
    )
    
    alert_threshold = models.IntegerField(
        _("Alert Threshold"),
        default=10,
        help_text=_("Percentage variance to trigger stock alerts")
    )

    # System Integration
    external_system_id = models.CharField(
        _("External ID"),
        max_length=200,
        blank=True,
        null=True,
        # editable=False
        help_text=_("Identifier in external ERP/WMS systems")
    )
    
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("Last Updated By"),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text=_("User who last modified policies")
    )

class InventoryProperty(InventoryPolicy):
    class Meta:
        abstract=True

    assembly = models.BooleanField(
        default=False,
        verbose_name=_('Assembly'),
        help_text=_('Can this Inventory be built from other Inventory?'),
    )

    component = models.BooleanField(
        default=False,
        verbose_name=_('Component'),
        help_text=_('Can this Inventory be used to build other Inventory?'),
    )

    trackable = models.BooleanField(
        default=True,
        verbose_name=_('Trackable'),
        help_text=_('Does this Inventory have tracking for unique items?'),
    )

    testable = models.BooleanField(
        default=False,
        verbose_name=_('Testable'),
        help_text=_('Can this Inventory have test results recorded against it?'),
    )

    purchaseable = models.BooleanField(
        default=True,
        verbose_name=_('Purchaseable'),
        help_text=_('Can this Inventory be purchased from external suppliers?'),
    )

    salable = models.BooleanField(
        default=True,
        verbose_name=_('Salable'),
        help_text=_('Can this Inventory be sold to customers?'),
    )

    active = models.BooleanField(
        default=True, verbose_name=_('Active'), help_text=_('Is this Inventory active?')
    )

    locked = models.BooleanField(
        default=False,
        verbose_name=_('Locked'),
        help_text=_('Locked Inventory cannot be edited'),
    )

    virtual = models.BooleanField(
        default=False,
        verbose_name=_('Virtual'),
        help_text=_('Is this a virtual inventory, such as a software product or license?'),
    )





class InventoryCategory(MPTTModel):
    
    structural = models.BooleanField(
        default=False,
        verbose_name=_('Structural'),
        help_text=_(
            'Inventory may not be directly assigned to a structural category, '
            'but may be assigned to child categories.'
        ),
    )
    default_location = TreeForeignKey(
        'stock.StockLocation',
        related_name='default_categories',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name=_('Default Location'),
        help_text=_('Default location for parts in this category'),
    )
    name = models.CharField(
        max_length=200, 
        unique=True, 
        help_text='It must be unique', 
        verbose_name='Category name*'
    )
    profile=models.ForeignKey(
        CompanyProfile,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        editable=False,
        related_name='inventory_categories',
        related_query_name='inventory_category'

    )
    slug = models.SlugField(max_length=230, editable=False)
    is_active = models.BooleanField(default=True)
    parent = TreeForeignKey(
        "self",
        on_delete=models.SET_NULL,
        related_name="children",
        null=True,
        blank=True,
        verbose_name='Parent category',
        help_text=_('Parent  to which this category falls'),
    )
    description=models.TextField(blank=True,null=True)

    class MPTTMeta:

        order_insertion_by = ["name"]

    class Meta:

        ordering = ["name"]

        verbose_name_plural = _("categories")
        constraints=[
            models.UniqueConstraint(fields=['name','profile'],name='unique_name_profile')
        ]
    @classmethod
    def get_verbose_names(self,p=None):
        if str(p) =='0':
            return "Inventory Category"
        return "Inventory Categories"
    @property
    def get_label(self):
        return 'inventorycategory'
    @classmethod
    def return_numbers(self,profile) :
        return self.objects.filter(profile=profile).count()



    def save(self, *args, **kwargs):

        self.slug = f"{get_random_string(6)}{slugify(self.name)}-{self.pk}-{get_random_string(5)}"

        super(InventoryCategory, self).save(*args, **kwargs)


    def __str__(self):
        return self.name
    @classmethod
    def tabular_display(self):
        return [{"name":'Name'}, {'is_active':'Active'}]


class Inventory(InventoryProperty):
    """
    Represents a complete inventory system within an organization.
    Tracks all aspects of inventory management including stock items,
    categorization, and policy enforcement.
    
    Attributes:
        name (str): Unique identifier for the inventory system
        description (str): Detailed operational context for the inventory
        category (InventoryCategory): Hierarchical classification
        profile (CompanyProfile): Owning organization
        inventory_type (TypeOf): Operational classification type
    """
    

    name = models.CharField(
        _("Inventory Name"),
        max_length=255,
        help_text=_("Unique identifier for this inventory system")
    )
    
    description = models.TextField(
        _("Description"),
        blank=True,
        null=True,
        help_text=_("Detailed operational context and usage notes")
    )
    default_supplier = models.ForeignKey(
        'company.Company',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name=_('Default Supplier'),
        help_text=_('Default supplier For the Inventory'),
        related_name='default_inventories',
        limit_choices_to={'is_supplier': True},

    )
    
    inventory_type = models.ForeignKey(
        TypeOf,
        verbose_name=_("Inventory Type"),
        on_delete=models.SET_NULL,
        null=True,
        limit_choices_to={'which_model': 'inventory'},
        help_text=_("Classification based on operational purpose")
    )
    
    profile = models.ForeignKey(
        CompanyProfile,
        verbose_name=_("Owning Organization"),
        on_delete=models.CASCADE,
        null=True,
        related_name='inventories',
        help_text=_("Organization responsible for this inventory")
    )
    
    category = models.ForeignKey(
        InventoryCategory,
        verbose_name=_("Classification Category"),
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='inventories',
        help_text=_("Hierarchical grouping for inventory items")
    )
    
    
    IPN = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_('IPN'),
        help_text=_('Internal Part Number'),
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("Created By"),
        on_delete=models.CASCADE,
        related_name='inventories',
        editable=False
    )

    
    officer_in_charge = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("Created By"),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='inventories_incharge',
        editable=False
    )
    
    created_at = models.DateTimeField(
        _("Creation Date"),
        auto_now_add=True
    )
    
    updated_at = models.DateTimeField(
        _("Last Updated"),
        auto_now=True
    )
    
    
    class Meta:
        verbose_name_plural = 'Inventories'
        ordering = ['-created_at']
        constraints=[
            models.UniqueConstraint(fields=['external_system_id','profile'],name='unique_inventory_external_system_id_profile')
        ]
    def generate_external_id(self):
        """Atomically generate unique external ID in PROFILE_INITIALS-SEQ format"""
        with transaction.atomic():
            profile = CompanyProfile.objects.select_for_update().get(pk=self.profile.pk)
            
            initials = ''.join([word[0] for word in profile.name.split() if word])[:3].upper()
            if len(initials) < 2:
                initials = profile.name[:2].upper()
                
            # Get and increment the sequence number atomically
            sequence_number = profile.inventory_sequence + 1
            profile.inventory_sequence = F('inventory_sequence') + 1
            profile.save(update_fields=['inventory_sequence'])
            
            # Refresh to get updated value
            profile.refresh_from_db()
            
            return f"{initials}-{self.category.pk}{self.profile.owner.pk}{self.profile.pk}-{profile.inventory_sequence:04d}"

    
    def save(self, *args, **kwargs):
        if not self.external_system_id:
            
            self.external_system_id = self.generate_external_id()
        super().save(*args, **kwargs)
    
    def clean(self):
        if self.minimum_stock_level> self.re_order_point:
            raise ValidationError({'minimum_stock_level': f'Minimum stock level {self.minimum_stock_level} cannot be greater than Reorder point {self.re_order_point}'})
        if self.re_order_point> self.re_order_quauntity:
            raise ValidationError({'re_order_point': f'Reorder stock level {self.re_order_point} cannot be greater than Reorder quantity {self.re_order_quauntity}'})
        if self.minimum_stock_level > self.re_order_point:
            raise ValidationError(...)
    
        if self.safety_stock_level < 0:
            raise ValidationError("Safety stock cannot be negative")
            
        if self.expiration_threshold < 0:
            raise ValidationError("Expiration threshold must be positive")
            
        if self.supplier_lead_time < 0:
            raise ValidationError("Lead time cannot be negative")

class InventoryManager(models.Manager):
    """
    - Custom manager for the Inventory model.
    - Provides methods for querying inventories.
    """

    def for_inventory(self, inventory):
        """
        - Get inventories associated with a specific inventory.

        - Args:
            - inventory (Inventory): The inventory to filter by.

        - Returns:
            - QuerySet: QuerySet of inventories associated with the specified inventory.
        """
        return self.get_queryset().filter(inventory=inventory)


class InventoryMixin(UUIDBaseModel):
    """
    Abstract model providing a common base for models associated with an inventory.

    - Attributes:
        - inventory (Inventory): The inventory to which the model belongs.

    - Manager:
        - objects (InventoryManager): Custom manager for querying objects based on inventory.
    """

    inventory = models.ForeignKey(Inventory, on_delete=models.CASCADE,null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = InventoryManager()

    class Meta:
        abstract = True
    
    def save(self, *args, **kwargs):
        """
        Override the save method to perform additional actions when saving.

        Args:
            - *args: Additional positional arguments.
            - **kwargs: Additional keyword arguments.
        """
        super().save(*args, **kwargs)

class InventoryPricing(InventoryMixin):

    currency = models.ForeignKey(
        Currency, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
        )
    scheduled_for_update = models.BooleanField(default=False)



    bom_cost_min = MoneyField(
        max_digits=15,
        decimal_places=2,
        default=0.0,
        null=True,
        blank=True,
        verbose_name=_('Minimum BOM Cost'),
        help_text=_('Minimum cost of component parts'),
    )

    bom_cost_max = MoneyField(
        max_digits=15,
        decimal_places=2,
        default=0.0,
        null=True,
        blank=True,
        verbose_name=_('Maximum BOM Cost'),
        help_text=_('Maximum cost of component parts'),
    )

    purchase_cost_min = MoneyField(
        max_digits=15,
        decimal_places=2,
        default=0.0,
        null=True,
        blank=True,
        verbose_name=_('Minimum Purchase Cost'),
        help_text=_('Minimum historical purchase cost'),
    )

    purchase_cost_max = MoneyField(
        max_digits=15,
        decimal_places=2,
        default=0.0,
        null=True,
        blank=True,
        verbose_name=_('Maximum Purchase Cost'),
        help_text=_('Maximum historical purchase cost'),
    )

    internal_cost_min = MoneyField(
        max_digits=15,
        decimal_places=2,
        default=0.0,
        null=True,
        blank=True,
        verbose_name=_('Minimum Internal Price'),
        help_text=_('Minimum cost based on internal price breaks'),
    )

    internal_cost_max = MoneyField(
        max_digits=15,
        decimal_places=2,
        default=0.0,
        null=True,
        blank=True,
        verbose_name=_('Maximum Internal Price'),
        help_text=_('Maximum cost based on internal price breaks'),
    )

    supplier_price_min = MoneyField(
        max_digits=15,
        decimal_places=2,
        default=0.0,
        null=True,
        blank=True,
        verbose_name=_('Minimum Supplier Price'),
        help_text=_('Minimum price of part from external suppliers'),
    )

    supplier_price_max = MoneyField(
        max_digits=15,
        decimal_places=2,
        default=0.0,
        null=True,
        blank=True,
        verbose_name=_('Maximum Supplier Price'),
        help_text=_('Maximum price of part from external suppliers'),
    )

    variant_cost_min = MoneyField(
        max_digits=15,
        decimal_places=2,
        default=0.0,
        null=True,
        blank=True,
        verbose_name=_('Minimum Variant Cost'),
        help_text=_('Calculated minimum cost of variant parts'),
    )

    variant_cost_max = MoneyField(
        max_digits=15,
        decimal_places=2,
        default=0.0,
        null=True,
        blank=True,
        verbose_name=_('Maximum Variant Cost'),
        help_text=_('Calculated maximum cost of variant parts'),
    )

    override_min = MoneyField(
        max_digits=15,
        decimal_places=2,
        default=0.0,
        null=True,
        blank=True,
        verbose_name=_('Minimum Cost'),
        help_text=_('Override minimum cost'),
    )

    override_max = MoneyField(
        max_digits=15,
        decimal_places=2,
        default=0.0,
        null=True,
        blank=True,
        verbose_name=_('Maximum Cost'),
        help_text=_('Override maximum cost'),
    )

    overall_min = MoneyField(
        max_digits=15,
        decimal_places=2,
        default=0.0,
        null=True,
        blank=True,
        verbose_name=_('Minimum Cost'),
        help_text=_('Calculated overall minimum cost'),
    )

    overall_max = MoneyField(
        max_digits=15,
        decimal_places=2,
        default=0.0,
        null=True,
        blank=True,
        verbose_name=_('Maximum Cost'),
        help_text=_('Calculated overall maximum cost'),
    )

    sale_price_min = MoneyField(
        max_digits=15,
        decimal_places=2,
        default=0.0,
        null=True,
        blank=True,
        verbose_name=_('Minimum Sale Price'),
        help_text=_('Minimum sale price based on price breaks'),
    )

    sale_price_max = MoneyField(
        max_digits=15,
        decimal_places=2,
        default=0.0,
        null=True,
        blank=True,
        verbose_name=_('Maximum Sale Price'),
        help_text=_('Maximum sale price based on price breaks'),
    )

    sale_history_min = MoneyField(
        max_digits=15,
        decimal_places=2,
        default=0.0,
        null=True,
        blank=True,
        verbose_name=_('Minimum Sale Cost'),
        help_text=_('Minimum historical sale price'),
    )

    sale_history_max = MoneyField(
        max_digits=15,
        decimal_places=2,
        default=0.0,
        null=True,
        blank=True,
        verbose_name=_('Maximum Sale Cost'),
        help_text=_('Maximum historical sale price'),
    )

class TransactionType(models.TextChoices):
    """Defines types of inventory transactions."""
    PO_RECEIVE = 'PO_RECEIVE', 'Purchase Order Receipt'
    PO_COMPLETE = 'PO_COMPLETE', 'Purchase Order Completion'
    ADJUSTMENT = 'ADJUSTMENT', 'Inventory Adjustment'
    SALE = 'SALE', 'Customer Sale'
    RETURN = 'RETURN', 'Inventory Return'
    LOSS = 'LOSS', 'Inventory Loss'
    
class InventoryTransaction(models.Model):
    
    profile= models.ForeignKey(
        CompanyProfile,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        editable=False,
        related_name='inventory_transactions',
    )

    item = models.ForeignKey(
        'stock.StockItem',
        on_delete=models.CASCADE,
        related_name='transactions'
    )
    quantity = models.IntegerField(
        help_text="Positive for additions, negative for deductions"
    )
    unit_price = MoneyField(
        max_digits=15,
        decimal_places=2,
        default=0.0,
        null=True,
        blank=True,
    )
    transaction_type = models.CharField(
        max_length=20,
        choices=TransactionType.choices,
        default='PO_COMPLETE'
    )
    reference = models.CharField(
        max_length=64,
        help_text="Associated document number (PO, SO, etc)"
    )
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='inventory_transactions'
    )
    notes = models.TextField(
        blank=True,
        help_text="Additional transaction details"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.transaction_type} - {self.item.name} ({self.quantity})"

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Inventory Transaction'
        verbose_name_plural = 'Inventory Transactions'
    

registerable_models=[Inventory,InventoryCategory,InventoryPricing,InventoryTransaction ]