"""Company database model definitions."""

import os

from decimal import Decimal


from django.core.validators import RegexValidator

from django.db import models
from django.contrib.contenttypes.fields import GenericRelation
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.utils.translation import pgettext_lazy as __
from mainapps.content_type_linking_models.models import Attachment
from mainapps.common.models import Address

from django_countries.fields import CountryField
from mainapps.inventory.helpers.field_validators import validate_currency_code
from mainapps.common.settings import  DEFAULT_CURRENCY_CODE, currency_code_mappings
from mainapps.inventory.helpers.file_editors import UniqueFilename
from mainapps.management.models import CompanyProfile



class Company(models.Model):
    """A Company object represents a company.

    It may be the owner's  or  supplier or a customer or a manufacturer (or a combination)

    - A supplier is a company from which parts can be purchased
    - A customer is a company to which parts can be sold
    - A manufacturer is a company which manufactures a raw good (they may or may not be a "supplier" also)


    - Attributes:
        - name: Brief name of the company
        - description: Longer form description
        - website: URL for the company website
        - address: One-line string representation of primary address
        - phone: contact phone number
        - email: contact email address
        - link: Secondary URL e.g. for link to internal Wiki page
        - image: Company image / logo
        - notes: Extra notes about the company
        - is_customer: boolean value, is this company owned by the user
        - is_customer: boolean value, is this company a customer
        - is_supplier: boolean value, is this company a supplier
        - is_manufacturer: boolean value, is this company a manufacturer
        - currency_code: Specifies the default currency for the company
    """

    class Meta:
        """Metaclass defines extra model options."""

        ordering = ['name']

        verbose_name_plural = 'Companies'

        constraints=[
            models.UniqueConstraint(fields=['name','profile'],name='unique_company_name_profile')
        ]
    
    name = models.CharField(
        max_length=100,
        blank=False,
        # help_text=_('Company name'),
        verbose_name=_('Company name'),
    )
    profile=models.ForeignKey(
        CompanyProfile,
        on_delete=models.SET_NULL,
        null=True,
        blank=False,
        editable=False,
        related_name='companies',
        related_query_name='company'


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
    
    is_customer = models.BooleanField(
        default=False,
        verbose_name=_('is customer'),
        help_text=_('Do you sell items to this company?'),
    )


    is_supplier = models.BooleanField(
        default=False,
        verbose_name=_('Is supplier'),
        help_text=_('Do you purchase items from this company?'),
    )

    is_manufacturer = models.BooleanField(
        default=False,
        verbose_name=_('is manufacturer'),
        help_text=_('Does this company manufacture parts?'),
    )

    

    currency = models.CharField(
        default=DEFAULT_CURRENCY_CODE,
        blank=True,
        max_length=12,
        verbose_name=_('Currency'),
        help_text=_('Default currency used for this company'),
        validators=[validate_currency_code],
        choices=currency_code_mappings(),
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True, related_name='companies_created',   
        editable=False

    )
    def get_user_label(self):
        return 'Affiliated Businesses'
    # def save(self,request, *args, **kwargs):
    #     if not self.pk:
    #         self.created_by = request.user
    #         # if self.is_owner:
    #         if self.created_by:
    #             print(self.created_by)
    #     super(Company, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return f'/company/company_detail/{self.pk}/'
    def __str__(self):
        if self.created_by:
            return f'{self.name} -> {self.created_by}'
        return self.name


class Contact(models.Model):
    """A Contact represents a person who works at a particular company. A Company may have zero or more associated Contact objects.

    Attributes:
        - company: Company link for this contact
        - name: Name of the contact
        - phone: contact phone number
        - email: contact email
        - role: position in company
    """

    alphanumeric_validator = RegexValidator(
        regex=r'^[a-zA-Z0-9]*$',
        message='Only alphanumeric characters are allowed.',
        code='invalid_alphanumeric'
    )

    company = models.ForeignKey(
        Company, related_name='contacts', on_delete=models.CASCADE, verbose_name='Company'
    )

    name = models.CharField(max_length=100, verbose_name='Name')

    phone = models.CharField(
        max_length=15, blank=True, verbose_name='Phone', validators=[alphanumeric_validator]
    )

    email = models.EmailField(blank=True, null=True,verbose_name='Email')

    role = models.CharField(
        max_length=100, blank=True, verbose_name='Role', help_text=_("Contact person role in company"),validators=[alphanumeric_validator]
    )


    class Meta:
        verbose_name_plural = 'Contacts'

    def __str__(self):
        return f"{self.name} - {self.company.name}"

class CompanyAddress(Address):
    """An address represents a physical location where the company is located. It is possible for a company to have multiple locations.

    Attributes:
        - company: Company link for this address
        - title: Human-readable name for the address
        - primary: True if this is the company's primary address
        - line1: First line of address
        - line2: Optional line two for address
        - postal_code: Postal code, city and state
        - country: Location country
        - shipping_notes: Notes for couriers transporting shipments to this address
        - internal_shipping_notes: Internal notes regarding shipping to this address
        - link: External link to additional address information
    """

    company = models.ForeignKey(
        Company,
        related_name='addresses',
        on_delete=models.CASCADE,
        verbose_name=_('Company'),
        help_text=_('Select company'),
        null=True,
        blank=False,

    )

    title = models.CharField(
        max_length=100,
        verbose_name=_('Address title'),
        help_text=_('Title describing the address entry'),
        blank=False,
    )

    primary = models.BooleanField(
        default=False,
        verbose_name=_('Primary address'),
        help_text=_('Set as primary or main address'),
    )
    

    shipping_notes = models.CharField(
        max_length=100,
        verbose_name=_('Courier shipping notes'),
        help_text=_('Notes for shipping courier'),
        blank=True,
    )

    internal_shipping_notes = models.CharField(
        max_length=100,
        verbose_name=_('Internal shipping notes'),
        help_text=_('Shipping notes for internal use'),
        blank=True,
    )

    link = models.URLField(
        blank=True,
        null=True,
        verbose_name=_('Link'),
        help_text=_('Link to address information (external)'),
    )

    class Meta:
        """Metaclass defines extra model options."""

        verbose_name_plural = 'Addresses'
        


    def __str__(self):
        return self.title


registerable_models=[CompanyAddress,Contact,Company]
