from django.db import models
from django.db.models import Q, Sum, Max
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.fields import GenericRelation
from django.utils import timezone
from django.db import transaction
from mainapps.management.models import CompanyProfile
from mptt.models import MPTTModel, TreeForeignKey

User = get_user_model()

class ProductAttribute(models.Model):
    """Global attribute definitions shared across products"""
    profile = models.ForeignKey(
        CompanyProfile,
        on_delete=models.CASCADE,
        null=True,
        related_name='attributes',
        help_text=_("Required company profile")
    )
    name = models.CharField(
        max_length=100,
        help_text=_("Attribute name (e.g. Color, Size)")
    )
    
    class Meta:
        unique_together = ('profile', 'name')
        ordering = ['name']
        verbose_name = _("Product Attribute")
        verbose_name_plural = _("Product Attributes")
    
    def __str__(self):
        return self.name

class ProductAttributeValue(models.Model):
    """Allowed values for attributes with uniqueness constraints"""
    attribute = models.ForeignKey(
        ProductAttribute,
        on_delete=models.CASCADE,
        related_name='values'
    )
    value = models.CharField(
        max_length=100,
        help_text=_("Specific attribute value (e.g. Red, 42)")
    )
    
    class Meta:
        unique_together = ('attribute', 'value')
        ordering = ['attribute__name', 'value']
        verbose_name = _("Attribute Value")
        verbose_name_plural = _("Attribute Values")

    def __str__(self):
        return f"{self.attribute.name}: {self.value}"

class PricingStrategy(models.Model):
    """Defines pricing calculation rules for products"""
    PRODUCT_MARGIN = 'margin'
    MARKET_MULTIPLIER = 'multiplier'
    FIXED_PRICE = 'fixed'
    
    STRATEGY_CHOICES = (
        (PRODUCT_MARGIN, _('Cost-Plus Margin')),
        (MARKET_MULTIPLIER, _('Market Multiplier')),
        (FIXED_PRICE, _('Fixed Price')),
    )
    
    strategy = models.CharField(
        max_length=20,
        choices=STRATEGY_CHOICES,
        default=PRODUCT_MARGIN
    )
    
    margin_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("Margin %"),
        help_text=_("Markup percentage (e.g. 30 for 30% margin)")
    )
    market_multiplier = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("Multiplier"),
        help_text=_("Multiply cost price by this value")
    )
    min_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("Minimum Price"),
        help_text=_("Price floor for automatic calculations")
    )
    max_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("Maximum Price"),
        help_text=_("Price ceiling for automatic calculations")
    )

    class Meta:
        verbose_name = _("Pricing Strategy")
        verbose_name_plural = _("Pricing Strategies")

    def clean(self):
        super().clean()
        if self.strategy == self.PRODUCT_MARGIN and not self.margin_percentage:
            raise ValidationError({
                'margin_percentage': _("Margin percentage is required for cost-plus strategy")
            })
        if self.strategy == self.MARKET_MULTIPLIER and not self.market_multiplier:
            raise ValidationError({
                'market_multiplier': _("Multiplier value is required for market multiplier strategy")
            })

class ProductCategory(MPTTModel):
    
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
        related_name='product_category',
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
            models.UniqueConstraint(fields=['name','profile'],name='unique_product_name_profile')
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





    def __str__(self):
        return self.name
    @classmethod
    def tabular_display(self):
        return [{"name":'Name'}, {'is_active':'Active'}]


class Product(models.Model):
    """Base product template with core pricing information"""
    profile = models.ForeignKey(
        CompanyProfile,
        on_delete=models.CASCADE,
        null=True,
        related_name='products',
        verbose_name=_("Company Profile")
    )
    created_by=models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='products_created',
        verbose_name=_("Created By")
    )
    created_at=models.DateTimeField(
        default=timezone.now,
        verbose_name=_("Created At")
    )
    updated_at=models.DateTimeField(
        auto_now=True,
        verbose_name=_("Updated At")
    )
    name = models.CharField(
        max_length=255,
        verbose_name=_("Product Name")
    )
    description = models.TextField(
        verbose_name=_("Description")
    )
    base_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_("Base Price"),
        help_text=_("Default selling price before modifiers")
    )
    is_template = models.BooleanField(
        default=True,
        verbose_name=_("Is Template"),
        help_text=_("Designates if this product is a template for variants")
    )
    attributes = models.ManyToManyField(
        ProductAttribute,
        through='ProductAttributeLink',
        related_name='products',
        verbose_name=_("Attributes")
    )
    unit = models.ForeignKey(
        'common.Unit',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name=_("Unit of Measure"),
        help_text=_("Required inventory unit (e.g. pieces, liters)")
    )
    pricing_strategy = models.OneToOneField(
        PricingStrategy,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='product',
        verbose_name=_("Pricing Strategy")
    )
    category= models.ForeignKey(
        ProductCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='products',
        verbose_name=_("Category")
    )

    class Meta:
        ordering = ['name']
        verbose_name = _("Product")
        verbose_name_plural = _("Products")
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['is_template']),
        ]

    def __str__(self):
        return self.name

    def next_variant_number(self):
        """Atomic sequence generator for variant numbers"""
        with transaction.atomic():
            variants = self.variants.select_for_update().all()
            current_max = variants.aggregate(Max('variant_number'))['variant_number__max']
            return (current_max or 0) + 1

    @property
    def current_cost_price(self):
        """Average cost of active inventory batches"""
        return self.variants.aggregate(
            avg_cost=models.Avg('purchase_history__purchase_price',
                         filter=Q(purchase_history__effective_end__isnull=True))
        )['avg_cost']

    def calculate_dynamic_price(self):
        """Strategy-based price calculation"""
        if not self.pricing_strategy or self.pricing_strategy.strategy == PricingStrategy.FIXED_PRICE:
            return self.base_price

        cost = self.current_cost_price
        if not cost:
            return self.base_price

        strategy = self.pricing_strategy
        if strategy.strategy == PricingStrategy.PRODUCT_MARGIN:
            new_price = cost * (1 + strategy.margin_percentage / 100)
        elif strategy.strategy == PricingStrategy.MARKET_MULTIPLIER:
            new_price = cost * strategy.market_multiplier
        else:
            new_price = self.base_price

        # Apply price constraints
        if strategy.min_price:
            new_price = max(new_price, strategy.min_price)
        if strategy.max_price:
            new_price = min(new_price, strategy.max_price)

        return round(new_price, 2)

    def update_base_price(self, commit=True):
        """Update base price with audit trail"""
        new_price = self.calculate_dynamic_price()
        if new_price != self.base_price:
            PriceChangeHistory.objects.create(
                product=self,
                old_price=self.base_price,
                new_price=new_price,
                change_type='auto'
            )
            self.base_price = new_price
            if commit:
                self.save()
        return self.base_price

class ProductAttributeLink(models.Model):
    """Links attributes to products with pricing modifiers"""
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='attribute_links'
    )

    attribute = models.ForeignKey(
        ProductAttribute,
        on_delete=models.CASCADE,
        related_name='product_links'
    )
    required = models.BooleanField(
        default=True,
        verbose_name=_("Required"),
        help_text=_("Is this attribute required for variants?")
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Ordering Priority")
    )
    default_modifier = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name=_("Price Modifier"),
        help_text=_("Default price adjustment for this attribute")
    )

    class Meta:
        ordering = ['order']
        unique_together = ('product', 'attribute')
        verbose_name = _("Product Attribute Link")
        verbose_name_plural = _("Product Attribute Links")
        indexes = [
            models.Index(fields=['product', 'order']),
            models.Index(fields=['attribute']),
        ]

    def __str__(self):
        return f"{self.product} - {self.attribute}"

class ProductVariant(models.Model):
    """Concrete product variation with specific attributes"""
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='variants',
        verbose_name=_("Parent Product")
    )
    
    sku = models.CharField(
        max_length=100,
        unique=True,
        verbose_name=_("SKU"),
        help_text=_("Automatically generated stock keeping unit")
    )
    active = models.BooleanField(
        default=True,
        verbose_name=_("Active"),
        help_text=_("Available for sale")
    )
    variant_number = models.PositiveIntegerField(
        editable=False,
        verbose_name=_("Variant Sequence")
    )

    attachments = GenericRelation(
        'common.Attachment',
        content_type_field='content_type',
        object_id_field='object_id',
        related_query_name='variant'
    )

    class Meta:
        ordering = ['product__name', 'variant_number']
        verbose_name = _("Product Variant")
        verbose_name_plural = _("Product Variants")
        indexes = [
            models.Index(fields=['sku']),
            models.Index(fields=['active']),
            models.Index(fields=['product', 'active']),
        ]

    def __str__(self):
        return f"{self.product.name} - Variant {self.variant_number}"

    @cached_property
    def selling_price(self):
        """Current selling price with cached result"""
        return self.product.base_price + sum(
            attr.effective_modifier for attr in self.attributes.all()
        )

    @property
    def total_stock(self):
        """Aggregate inventory quantity"""
        return self.stock_items.aggregate(
            total=Sum('quantity')
        )['total'] or 0

    def save(self, *args, **kwargs):
        if not self.pk:
            if not self.product.profile:
                raise ValidationError(_("Product must have a company profile to create variants"))
            self.variant_number = self.product.next_variant_number()
            self.sku = self.generate_sku()
        super().save(*args, **kwargs)

    def generate_sku(self):
        """Generate standardized SKU format"""
        return (
            f"C{self.product.profile.id:04d}-"
            f"P{self.product.id:06d}-"
            f"V{self.variant_number:04d}"
        )

class ProductVariantAttribute(models.Model):
    """Variant-specific attribute selections with pricing"""
    variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.CASCADE,
        related_name='attributes'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        editable=False
    )
    attribute_link = models.ForeignKey(
        ProductAttributeLink,
        on_delete=models.CASCADE,
        related_name='variant_attributes'
    )
    value = models.ForeignKey(
        ProductAttributeValue,
        on_delete=models.PROTECT,
        related_name='variant_attributes'
    )
    custom_modifier = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("Custom Modifier"),
        help_text=_("Override default price modifier")
    )

    class Meta:
        unique_together = ('variant', 'attribute_link')
        verbose_name = _("Variant Attribute")
        verbose_name_plural = _("Variant Attributes")
        indexes = [
            models.Index(fields=['variant', 'attribute_link']),
        ]

    def clean(self):
        if self.value.attribute != self.attribute_link.attribute:
            raise ValidationError(_("Attribute value must match attribute link"))

    def save(self, *args, **kwargs):
        if not self.product_id:
            self.product = self.variant.product
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def effective_modifier(self):
        return self.custom_modifier or self.attribute_link.default_modifier

class PriceChangeHistory(models.Model):
    """Audit trail for price modifications"""
    APPROVAL_STATUS = (
        ('pending', _("Pending")),
        ('approved', _("Approved")),
        ('rejected', _("Rejected")),
    )
    
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='price_history'
    )
    old_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_("Previous Price")
    )
    new_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_("New Price")
    )
    changed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Changed By")
    )
    change_type = models.CharField(
        max_length=20,
        choices=(
            ('auto', _("Automatic")),
            ('manual', _("Manual")),
            ('override', _("Override")),
        ),
        verbose_name=_("Change Type")
    )
    status = models.CharField(
        max_length=20,
        choices=APPROVAL_STATUS,
        default='pending',
        verbose_name=_("Approval Status")
    )
    timestamp = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Timestamp")
    )
    reason = models.TextField(
        blank=True,
        verbose_name=_("Change Reason")
    )

    class Meta:
        ordering = ['-timestamp']
        verbose_name = _("Price Change History")
        verbose_name_plural = _("Price Change Histories")
        indexes = [
            models.Index(fields=['product', 'timestamp']),
        ]

    def __str__(self):
        return f"{self.product} price change {self.old_price}→{self.new_price}"

class PurchasePriceHistory(models.Model):
    """Historical record of inventory acquisition costs"""
    variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.CASCADE,
        related_name='purchase_history'
    )
    purchase_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_("Unit Cost")
    )
    effective_start = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Effective Start")
    )
    effective_end = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Effective End")
    )
    source = models.ForeignKey(
        'orders.PurchaseOrderLineItem',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Source Order")
    )

    class Meta:
        ordering = ['-effective_start']
        verbose_name = _("Purchase Price History")
        verbose_name_plural = _("Purchase Price Histories")
        indexes = [
            models.Index(fields=['variant', '-effective_start']),
        ]

    def __str__(self):
        return f"{self.variant} @ {self.purchase_price}"
    
class PricingRule(models.Model):
    RULE_TYPES = (
        ('BATCH', 'Stock Batch Override'),
        ('CUSTOMER', 'Customer Specific'),
        ('PROMO', 'Time-Limited Promotion'),
        ('VOLUME', 'Volume Discount')
    )
    
    rule_type = models.CharField(max_length=20, choices=RULE_TYPES)
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE)
    value = models.DecimalField(max_digits=10, decimal_places=2)
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    min_quantity = models.PositiveIntegerField(null=True, blank=True)
    
    def is_active(self):
        from django.utils import timezone
        now = timezone.now()
        return (self.start_date <= now <= self.end_date) if self.start_date else True