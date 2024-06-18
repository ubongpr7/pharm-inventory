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

from mainapps.common.models import TypeOf, Unit
from mainapps.content_type_linking_models.models import UUIDBaseModel
from mainapps.management.models import CompanyProfile, InventoryPolicy






class InventoryCategory(MPTTModel):

    name = models.CharField(
        max_length=200, 
        unique=True, 
        help_text='It must be unique', 
        verbose_name='Category name*'
    )
    profile=models.ForeignKey(
        CompanyProfile,
        on_delete=models.SET_NULL,
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
        on_delete=models.PROTECT,
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
        # if self.profile:
            # return f'{self.name} {self.profile}'
        return self.name
    @classmethod
    def tabular_display(self):
        return ['Name', 'Active','Parent','Descrition']



class Inventory(InventoryPolicy):
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
        constraints=[
            models.UniqueConstraint(fields=['name','profile'],name='unique_inventory_name_profile')
        ]
    @classmethod
    def get_verbose_names(self,p=None):
        if str(p) =='0':
            return "Inventory "
        return "Inventories "
    @property
    def get_label(self):
        return 'inventory'
    @classmethod
    def return_numbers(self,profile) :
        return self.objects.filter(profile=profile).count()
    @classmethod
    def tabular_display(self):
        return ['Name', 'Type','Category','Created by','Created at','Last update','Items unit','Minimum stock level', 'Reorder point','Reorder quauntity','Recall policy','Expiration policy' ]


    name = models.CharField(
        max_length=255,
        blank=False,
        verbose_name='Inventory name*'
    
    )
    i_type=models.ForeignKey(
        TypeOf,
        on_delete=models.SET_NULL,
        null=True,
        blank=False,
        limit_choices_to={'which_model':'inventory'},
        verbose_name='Type of  inventory*',
    )
    
    profile=models.ForeignKey(
        CompanyProfile,
        on_delete=models.SET_NULL,
        null=True,
        blank=False,
        editable=False,
        related_name='inventories',
        related_query_name='inventory'


    )
    
    description = models.TextField(null=True,blank=True)
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
    unit = models.ForeignKey(
        Unit, 
        on_delete=models.SET_NULL, 
        blank=True,
        verbose_name='Unit of measurement',
        help_text='Set unit for items in this inventory e.g pieces,cm,m...',
        null=True,
        related_name='inventories'
    )
    
    def get_absolute_url(self):
        return f'/inventory/details/{self.pk}/'
    def __str__(self):
        return f'{self.name} '
    
    def clean(self):
        if self.minimum_stock_level> self.re_order_point:
            raise ValidationError({'minimum_stock_level': f'Minimum stock level {self.minimum_stock_level} cannot be greater than Reorder point {self.re_order_point}'})
        if self.re_order_point> self.re_order_quauntity:
            raise ValidationError({'re_order_point': f'Reorder stock level {self.re_order_point} cannot be greater than Reorder quantity {self.re_order_quauntity}'})

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

    inventory = models.ForeignKey(Inventory, on_delete=models.SET_NULL,null=True)

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


 



registerable_models=[Inventory,InventoryCategory]