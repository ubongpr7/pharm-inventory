from django.db import models
import uuid 
from django.conf import settings
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.utils.translation import pgettext_lazy as __
from django.db.models import UniqueConstraint
from django.contrib.contenttypes.fields import GenericRelation
from django.utils.text import slugify
from django.core.signing import Signer
from django.contrib.auth.models import Permission
from mainapps.content_type_linking_models.models import Attachment
from mainapps.common.models import Country, TypeOf
from mainapps.inventory.helpers.field_validators import validate_currency_code
from mainapps.common.settings import  DEFAULT_CURRENCY_CODE, currency_code_mappings
from mainapps.inventory.helpers.file_editors import UniqueFilename
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

# Create your models here.
signer=Signer()
class CompanyProfile(models.Model):
    class Meta:
        """Metaclass defines extra model options."""

        ordering = ['name']
        constraints = [
            UniqueConstraint(fields=['name',], name='unique_name')
        ]

        verbose_name_plural = 'Company Profile'

    unique_id = models.CharField(max_length=15, unique=True,editable=False, default=str(uuid.uuid4().int)[:15])
    name = models.CharField(
        max_length=100,
        blank=False,
        unique=True,
        verbose_name=_('Company name'),
    )
    slug=models.SlugField(
        unique=True,
        null=True,
        editable=False
    )
    industry=models.ForeignKey(
        TypeOf,
        on_delete=models.SET_NULL,
        null=True,
        blank=False,
        limit_choices_to={'which_model':'industry'}

    )
    description = models.CharField(
        max_length=1000,
        verbose_name=_('Company description'),
        help_text=_('Briefly describe the company'),
        blank=True,
        null=True,
    )

    website = models.URLField(
        blank=True, verbose_name=_('Website'), help_text=_('Company website URL (optional)')
    )

    phone = models.CharField(
        max_length=15,
        verbose_name=_('Phone number'),
        blank=True,
        help_text=_('Contact phone number (optional)'),
    )

    email = models.EmailField(
        blank=True,
        null=True,
        verbose_name=_('Email'),
        help_text=_('Contact email address (optional)'),
    )
    
    link = models.URLField(
        blank=True,
        verbose_name=_('Link/Website'),
        help_text=_('Link to external company information or profile'),
    )

    attachment= GenericRelation(Attachment,  related_query_name='companies')
    
    
    currency = models.CharField(
        default=DEFAULT_CURRENCY_CODE,
        blank=True,
        max_length=12,
        verbose_name=_('Base Currency'),
        help_text=_('Set company default currency'),
        validators=[validate_currency_code],
        choices=currency_code_mappings(),
    )

    owner = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='company',
        blank=True, 
        editable=False

    )
    @property
    def encrypted_id( self):
        return signer.sign(self.unique_id)

    @property
    def decrypted_id(self ):
        return signer.unsign(self.unique_id)

    def save(self,*args,**kwargs) :
        if self.name:
            self.slug=slugify(self.name)
        super(CompanyProfile, self).save(*args, **kwargs)
    def __str__(self):
        if self.owner:

            return f'{self.name} -> {self.unique_id} {self.owner.email}' 
        return f'{self.name } -> {self.unique_id}'



class Policy(models.Model):
    name = models.CharField(
        max_length=100,
        blank=False,
        unique=True,
        verbose_name=_('Policy name'),
    )

    details = models.TextField(
        blank=False,
        unique=True,
        verbose_name=_('Details of the policy'),
    )

    company=models.ForeignKey(
        CompanyProfile,
        on_delete=models.CASCADE,
    )
    effective_date=models.DateField(
        null=True,
    )
    expiration_date=models.DateField(
        null=True,
    )
    updated_at=models.DateTimeField(auto_now=True)
    class Meta:
        abstract=True


class InventoryPolicy(models.Model):
    minimum_stock_level=models.IntegerField(default=0, help_text='Minimum stock level before you receive alert')
    re_order_point=models.IntegerField(default=10, help_text='At what point can reorder activities be triggered ')
    automate_reorder=models.BooleanField(
        default=False,
        help_text=_('If product reaches reoder point, do you want an automated reorder processing ')
    
    )
    re_order_quauntity=models.IntegerField(default=200,)
    class RecallPolicies(models.TextChoices):
        remove=0,'Remove from stock'
        notify_cust=1,'Notify customers'
        replace_product=3,'Replace item'
        destroy=4,'Destroy item'
        repair=5,'Repair item'
    class ExpirePolicies(models.TextChoices):
        remove=0,'Dispose of stock'
        return_m=1,'Return to manufacturer'
        
    recall_policy=models.CharField(
        max_length=200,
        choices=RecallPolicies.choices,
        default=RecallPolicies.remove,
        help_text=_('What happens if product is bad')

    )
    expiration_policy=models.CharField(
        max_length=200,
        choices=ExpirePolicies.choices,
        default=ExpirePolicies.remove,
        help_text=_('What happens if product expires')


    )
    class Meta:
        abstract=True


class PrescriptionFillingPolicies(Policy):
    validity_period=models.IntegerField(
        default=5,
        help_text='Prescription is valid before how many days',
    )
    quantitity_limit=models.IntegerField(
    )
    refills_allowed=models.IntegerField(
        # help_text='Prescription is valid before how many days',
    )
registerable_models=[CompanyProfile,PrescriptionFillingPolicies,]    