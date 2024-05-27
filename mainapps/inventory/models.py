import uuid
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.contrib.auth.models import Permission
from django.contrib.auth.models import Group
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.conf import settings
from mptt.models import MPTTModel, TreeForeignKey
from django.utils.crypto import get_random_string
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from mainapps.common.models import User
from mainapps.company.models import Company






class InventoryCategory(MPTTModel):

    name = models.CharField(
        max_length=200, 
        unique=True, 
        help_text='It must be unique', 
        verbose_name='Category'
    )
    slug = models.SlugField(max_length=230, editable=False)
    is_active = models.BooleanField(default=True)
    parent = TreeForeignKey(
        "self",
        on_delete=models.PROTECT,
        related_name="children",
        null=True,
        blank=True
    )
    description=models.TextField(blank=True,null=True)

    class MPTTMeta:

        order_insertion_by = ["name"]

    class Meta:

        ordering = ["name"]

        verbose_name_plural = _("categories")




    def save(self, *args, **kwargs):

        self.slug = f"{get_random_string(6)}{slugify(self.name)}-{self.pk}-{get_random_string(5)}"

        super(InventoryCategory, self).save(*args, **kwargs)


    def __str__(self):

        return self.name




class Inventory(models.Model):
    """
    - Represents an inventory in the system.
    - Attributes:
        - name (str): The name of the inventory.
        - description (str): A detailed description of the inventory.
        - created_by (User): The user who created the inventory.
        - created_at (DateTime): The date and time when the inventory was created.
        - updated_at (DateTime): The date and time when the inventory was last updated.
        - category (Category): The category to which the inventory belongs.
        - organisation 
    """
    class Meta:
        verbose_name_plural = 'Inventories'
        ordering = ['-created_at']

    name = models.CharField(max_length=255)
    description = models.TextField()
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='inventories',
        editable=False
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    category = models.ForeignKey(
        InventoryCategory, 
        on_delete=models.SET_NULL, 
        blank=True,
        null=True,
        related_name='inventories'
    )
    company=models.ForeignKey(
        Company,
        null=True,
        blank=True,
        limit_choices_to={'is_owner': True},

       on_delete=models.SET_NULL,
    )
    
    def get_absolute_url(self):
        return f'/inventory/details/{self.pk}/'
    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.pk:
            self.created_by = self.request.user
            # if self.created_by:
            #     if self.created_by.company:
            #         self.company=self.created_by.company
        super(Inventory, self).save(*args, **kwargs)

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


class InventoryMixin(models.Model):
    """
    Abstract model providing a common base for models associated with an inventory.

    - Attributes:
        - inventory (Inventory): The inventory to which the model belongs.

    - Manager:
        - objects (InventoryManager): Custom manager for querying objects based on inventory.
    """

    inventory = models.ForeignKey(Inventory, on_delete=models.CASCADE)

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


 



class PermissionLog(InventoryMixin):
    """
    Represents a log entry for user actions within an inventory.

    Attributes:
        - user (ForeignKey): The user associated with the action.
        - content_type (ForeignKey): The content type of the related object (Inventory, in this case).
        - object_id (PositiveIntegerField): The ID of the related object.
        - inventory (GenericForeignKey): Generic relation to the related inventory.
        - action (str): The action performed by the user (e.g., View, Edit, Delete).
        - timestamp (DateTime): The date and time when the action occurred.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    action = models.CharField(max_length=50)
    timestamp = models.DateTimeField(auto_now_add=True)


registerable_models=[PermissionLog,Inventory,InventoryCategory]