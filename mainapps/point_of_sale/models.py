from django.db import models, transaction
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.core.validators import MinValueValidator
from django.db.models import F, ExpressionWrapper, DecimalField
from decimal import Decimal
import uuid

User = get_user_model()

class SyncMixin(models.Model):
    """
    Abstract base model for enabling synchronization support.

    Fields:
        - sync_identifier: Unique identifier used for syncing across systems.
        - is_synced: Indicates whether the instance has been synced with the server.
        - last_sync_attempt: Timestamp of the last attempt to sync.
        - sync_version: Integer counter for sync versioning (useful for conflict resolution).
    """
    sync_identifier = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)
    is_synced = models.BooleanField(default=False, db_index=True)
    last_sync_attempt = models.DateTimeField(null=True, blank=True)
    sync_version = models.PositiveIntegerField(default=0)

    class Meta:
        abstract = True




class POSTerminal(SyncMixin, models.Model):
    """
    Represents a physical or virtual POS terminal.
    
    Fields:
        - name: Friendly name for the terminal (e.g., "Cashier 1").
        - location: Associated stock location.
        - is_online: Indicates if the terminal is online or offline.
    """
    name = models.CharField(max_length=100)
    location = models.ForeignKey('stock.Location', on_delete=models.PROTECT, to_field='sync_identifier')
    is_online = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({'Online' if self.is_online else 'Offline'})"


class ConflictLog(models.Model):
    """
    Logs data conflicts during synchronization between local and remote databases.

    Fields:
        - model_name: The name of the model where the conflict occurred.
        - local_data: The local version of the data.
        - remote_data: The remote version of the data.
        - resolved_data: The final resolved version after conflict handling.
        - resolution: How the conflict was resolved (local, remote, merged).
        - created_at: When the conflict occurred.
        - resolved_at: When the conflict was resolved.
    """
    model_name = models.CharField(max_length=255)
    local_data = models.JSONField()
    remote_data = models.JSONField()
    resolved_data = models.JSONField(null=True, blank=True)
    resolution = models.CharField(
        max_length=20,
        choices=[
            ('local_wins', 'Local Version Kept'),
            ('remote_wins', 'Remote Version Applied'),
            ('merged', 'Data Merged')
        ]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)


class POSSession(SyncMixin, models.Model):
    """
    A POS session representing a cashier or terminal session.

    Fields:
        - id: UUID as primary key.
        - terminal: Linked terminal where session took place.
        - user: User who opened the session.
        - opening_time / closing_time: Time markers for session lifecycle.
        - opening_balance: Starting cash amount.
        - calculated_balance: System-calculated total at closing.
        - discrepancy: Difference between actual and expected balance.
        - inventory_snapshot: JSON snapshot of inventory at session start.
        - offline_operations: List of actions queued for sync.

    Notes:
        - Automatically captures inventory on creation.
        - Logs 'session_create' if the terminal is offline.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    terminal = models.ForeignKey('POSTerminal', on_delete=models.PROTECT, to_field='sync_identifier')
    user = models.ForeignKey(User, on_delete=models.PROTECT, to_field='uuid')
    opening_time = models.DateTimeField(auto_now_add=True)
    closing_time = models.DateTimeField(null=True, blank=True)
    opening_balance = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))])
    calculated_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discrepancy = models.DecimalField(max_digits=10, decimal_places=2, default=0, editable=False)
    inventory_snapshot = models.JSONField(editable=False)
    offline_operations = models.JSONField(default=list)

    class Meta:
        indexes = [
            models.Index(fields=['opening_time', 'terminal']),
            models.Index(fields=['is_synced', 'last_sync_attempt'])
        ]

    def save(self, *args, **kwargs):
        if not self.pk:
            self.inventory_snapshot = self._get_inventory_snapshot()
            if not self.terminal.is_online:
                self.offline_operations.append('session_create')
        super().save(*args, **kwargs)

    def _get_inventory_snapshot(self):
        from stock.models import StockItem
        return {
            'items': list(StockItem.objects.filter(
                location=self.terminal.location
            ).values('sync_identifier', 'quantity', 'reserved'))
        }


class POSOrder(SyncMixin, models.Model):
    """
    A POS order that belongs to a session and adjusts inventory on finalization.

    Fields:
        - id: UUID as primary key.
        - session: Associated POSSession.
        - location: Stock location involved in the order.
        - created_at / finalized_at: Time markers.
        - total: Order total.
        - inventory_adjusted: Whether stock levels have been updated.
        - pending_sync_operations: Deferred actions due to offline status.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    STATUS_CHOICES = [
        ('draft', _('Draft')),
        ('finalized', _('Finalized')),
        ('void', _('Void'))
    ]
    session = models.ForeignKey(POSSession, on_delete=models.PROTECT, to_field='sync_identifier')
    location = models.ForeignKey('stock.Location', on_delete=models.PROTECT, to_field='sync_identifier')
    created_at = models.DateTimeField(auto_now_add=True)
    finalized_at = models.DateTimeField(null=True, blank=True)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    inventory_adjusted = models.BooleanField(default=False)
    pending_sync_operations = models.JSONField(default=list)

    class Meta:
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['sync_identifier', 'is_synced'])
        ]

    def finalize_order(self):
        """Finalize the order, adjust inventory, and mark as finalized."""
        with transaction.atomic():
            self._queue_inventory_adjustment()
            self._process_payments()
            self.status = 'finalized'
            self.finalized_at = timezone.now()
            self.save()

    def _queue_inventory_adjustment(self):
        if self.location.terminal.is_online:
            self._adjust_inventory()
        else:
            self.pending_sync_operations.append({
                'operation': 'inventory_adjustment',
                'timestamp': timezone.now().isoformat()
            })


class POSOrderItem(SyncMixin, models.Model):
    """
    Line item in a POS order, representing one stock item sold.

    Fields:
        - id: UUID as primary key.
        - order: The POSOrder this item belongs to.
        - stock_item: The inventory item sold.
        - quantity: Quantity sold (min 0.001).
        - captured_price: Sale price per unit at transaction time.
        - captured_cost: Cost price at the time.
        - tax_profile: Associated tax rate/profile.
        - line_total: Auto-calculated field (quantity * price).
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(POSOrder, on_delete=models.CASCADE, related_name='items', to_field='sync_identifier')
    stock_item = models.ForeignKey('stock.StockItem', on_delete=models.PROTECT, to_field='sync_identifier')
    quantity = models.DecimalField(max_digits=10, decimal_places=3, validators=[MinValueValidator(Decimal('0.001'))])
    captured_price = models.DecimalField(max_digits=10, decimal_places=2)
    captured_cost = models.DecimalField(max_digits=10, decimal_places=2)
    tax_profile = models.ForeignKey('TaxProfile', on_delete=models.PROTECT, to_field='sync_identifier')
    line_total = models.GeneratedField(
        expression=ExpressionWrapper(
            F('quantity') * F('captured_price'),
            output_field=DecimalField(max_digits=12, decimal_places=2)
        ),
        db_persist=True
    )

    class Meta:
        constraints = [
            models.CheckConstraint(check=models.Q(quantity__gt=0), name='positive_quantity')
        ]


class IntegratedPayment(SyncMixin, models.Model):
    """
    Represents a payment made through an external payment gateway.

    Fields:
        - id: UUID primary key.
        - order: POSOrder linked to this payment.
        - gateway: The payment gateway used (e.g., Paystack, Stripe).
        - amount: Amount paid.
        - transaction_id: Gateway-provided reference ID.
        - synced_with_accounting: Whether this payment has been reconciled with accounting.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(POSOrder, on_delete=models.PROTECT, to_field='sync_identifier')
    gateway = models.ForeignKey('payment.PaymentGateway', on_delete=models.PROTECT, to_field='sync_identifier')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_id = models.CharField(max_length=255)
    synced_with_accounting = models.BooleanField(default=False)

    class Meta:
        indexes = [
            models.Index(fields=['transaction_id']),
            models.Index(fields=['sync_identifier', 'is_synced'])
        ]


class SyncManager(models.Model):
    """
    Tracks the global sync state for a specific device.

    Fields:
        - last_successful_sync: Timestamp of last successful sync.
        - pending_operations: Number of pending operations to be synced.
        - sync_state: JSON of ongoing sync status.
        - device_identifier: UUID of the current device.
    """
    last_successful_sync = models.DateTimeField(null=True, blank=True)
    pending_operations = models.PositiveIntegerField(default=0)
    sync_state = models.JSONField(default=dict)
    device_identifier = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)


class IntegratedPayment(SyncMixin, models.Model):
    """
    Represents a partial or full payment made toward a POSOrder.
    Supports split payments across methods like cash, card, mobile, or QR.

    Fields:
        - order: The related POSOrder.
        - payment_method: Enum of methods used (cash, card, mobile, qr).
        - amount: Amount paid with this method.
        - transaction_ref: Optional external ref (e.g., card/QR transaction ID).
        - synced_with_accounting: Mark if synced with accounting system.
    """
    PAYMENT_METHODS = [
        ('cash', 'Cash'),
        ('card', 'Card'),
        ('mobile', 'Mobile Transfer'),
        ('qr', 'QR Code')
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(POSOrder, on_delete=models.CASCADE, related_name='payments', to_field='sync_identifier')
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHODS)
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    transaction_ref = models.CharField(max_length=255, null=True, blank=True)
    synced_with_accounting = models.BooleanField(default=False)

    class Meta:
        indexes = [
            models.Index(fields=['order', 'payment_method']),
            models.Index(fields=['sync_identifier', 'is_synced'])
        ]

    def __str__(self):
        return f"{self.payment_method} - ₦{self.amount}"
