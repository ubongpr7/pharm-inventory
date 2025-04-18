from django.db import models
from django.db.models import Sum
from mainapps.management.models import CompanyProfile

class ProductAttribute(models.Model):
    profile = models.ForeignKey(
        CompanyProfile,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='attributes'
    )
    name = models.CharField(max_length=100)
    
    class Meta:
        unique_together = ('profile', 'name')
    
    def __str__(self):
        return self.name

class ProductAttributeValue(models.Model):
    attribute = models.ForeignKey(
        ProductAttribute, 
        on_delete=models.CASCADE,
        related_name='values'
    )
    value = models.CharField(max_length=100)
    
    class Meta:
        unique_together = ('attribute', 'value')

    def __str__(self):
        return f"{self.attribute.name}: {self.value}"

class Product(models.Model):
    profile = models.ForeignKey(
        CompanyProfile,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        editable=False,
        related_name='products'
    )
    name = models.CharField(max_length=255)
    description = models.TextField()
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    is_template = models.BooleanField(default=True)
    attributes = models.ManyToManyField(
        ProductAttribute,
        through='ProductAttributeLink',
        related_name='products'
    )
    unit=models.ForeignKey(
        'common.Unit',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    def next_variant_number(self):
        """
        Get next variant sequence number for this product
        Uses database-level locking to prevent race conditions
        """
        from django.db.models import Max
        from django.db import transaction
        with transaction.atomic():
            # Lock product variants for atomic update
            variants = self.variants.select_for_update().all()
            current_max = variants.aggregate(Max('variant_number'))['variant_number__max']
            return (current_max or 0) + 1

class ProductAttributeLink(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    attribute = models.ForeignKey(ProductAttribute, on_delete=models.CASCADE)
    required = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    default_modifier = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )
    
    class Meta:
        ordering = ['order']
        unique_together = ('product', 'attribute')
        indexes = [
            models.Index(fields=['product', 'order']),
            models.Index(fields=['attribute']),
        ]

class ProductVariant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    sku = models.CharField(max_length=100, unique=True)
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    active = models.BooleanField(default=True)
    variant_number = models.PositiveIntegerField(
        editable=False,
        default=0

    )

    class Meta:
        indexes = [
            models.Index(fields=['sku']),
            models.Index(fields=['active']),
        ]

    @property
    def price(self):
        return self.base_price + sum(
            attr.effective_modifier for attr in self.attributes.all()
        )

    @property
    def total_stock(self):
        return self.stock_items.aggregate(
            Sum('quantity')
        )['quantity__sum'] or 0
    def save(self, *args, **kwargs):
        """
        Auto-generate variant number and SKU on first save
        """
        if not self.pk:  
            self.variant_number = self.product.next_variant_number()
            
            self.sku = self.generate_sku()
            
        super().save(*args, **kwargs)

    def generate_sku(self):
        """
        Generate standardized SKU format:
        C<company_id>-P<product_id>-V<variant_number>
        Example: C123-P456-V0001
        """
        return (
            f"C{self.product.profile.id:04d}-"
            f"P{self.product.id:06d}-"
            f"V{self.variant_number:04d}"
        )
    
class ProductVariantAttribute(models.Model):
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, related_name='attributes')
    product = models.ForeignKey(  
        Product,
        on_delete=models.CASCADE,
        editable=False
    )
    attribute_link = models.ForeignKey(ProductAttributeLink, on_delete=models.CASCADE)
    value = models.ForeignKey(ProductAttributeValue, on_delete=models.CASCADE)
    custom_modifier = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )

    class Meta:
        unique_together = ('variant', 'attribute_link')

    def save(self, *args, **kwargs):
        if not self.product_id:
            self.product = self.variant.product
        super().save(*args, **kwargs)

    @property
    def effective_modifier(self):
        return (
            self.custom_modifier 
            if self.custom_modifier is not None 
            else self.attribute_link.default_modifier
        )