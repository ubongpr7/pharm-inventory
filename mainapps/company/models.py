"""Company database model definitions."""

import os

from decimal import Decimal

from django.utils.text import slugify

from django.db.models import UniqueConstraint
from django.core.validators import RegexValidator

from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import  UniqueConstraint
from django.contrib.contenttypes.fields import GenericRelation

from django.utils.translation import gettext_lazy as _
from django.utils.translation import pgettext_lazy as __

from mainapps.content_type_linking_models.models import Attachment
from mainapps.inventory.models import InventoryMixin
from mainapps.common.models import Country
from mainapps.inventory.helpers.field_validators import validate_currency_code
from mainapps.common.settings import  DEFAULT_CURRENCY_CODE, currency_code_mappings
from mainapps.inventory.helpers.file_editors import UniqueFilename



class Company(models.Model):
    """A Company object represents an external company.

    It may be a supplier or a customer or a manufacturer (or a combination)

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
        - is_customer: boolean value, is this company a customer
        - is_supplier: boolean value, is this company a supplier
        - is_manufacturer: boolean value, is this company a manufacturer
        - currency_code: Specifies the default currency for the company
    """

    class Meta:
        """Metaclass defines extra model options."""

        ordering = ['name']
        constraints = [
            UniqueConstraint(fields=['name'], name='unique_name')
        ]

        verbose_name_plural = 'Companies'


    name = models.CharField(
        max_length=100,
        blank=False,
        help_text=_('Company name'),
        verbose_name=_('Company name'),
    )

    description = models.CharField(
        max_length=1000,
        verbose_name=_('Company description'),
        help_text=_('Description of the company'),
        blank=True,
    )

    website = models.URLField(
        blank=True, verbose_name=_('Website'), help_text=_('Company website URL')
    )

    phone = models.CharField(
        max_length=15,
        verbose_name=_('Phone number'),
        blank=True,
        help_text=_('Contact phone number'),
    )

    email = models.EmailField(
        blank=True,
        null=True,
        verbose_name=_('Email'),
        help_text=_('Contact email address'),
    )

    contact = models.CharField(
        max_length=100,
        verbose_name=_('Contact'),
        blank=True,
        help_text=_('Point of contact'),
    )

    link = models.URLField(
        blank=True,
        verbose_name=_('Link'),
        help_text=_('Link to external company information or profile'),
    )

    attachment= GenericRelation(Attachment,  related_query_name='companies')

    is_customer = models.BooleanField(
        default=False,
        verbose_name=_('is customer'),
        help_text=_('Do you sell items to this company?'),
    )
    is_patiant = models.BooleanField(
        default=False,
        verbose_name=_('is patient'),
        help_text=_('Is this your regular patient'),
    )

    is_supplier = models.BooleanField(
        default=True,
        verbose_name=_('is supplier'),
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

class Address(models.Model):
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
        help_text=_('Set as primary address'),
    )

    street = models.CharField(
        max_length=50,
        verbose_name=_('Street'),
        help_text=_('Street number and name'),
        blank=True,
    )

    city = models.CharField(
        max_length=50,
        verbose_name=_('Town, City,'),
        help_text=_('Town and city'),
        blank=True,
    )
    state = models.CharField(
        max_length=50,
        verbose_name=_('State or province '),
        help_text=_('State located'),
        blank=True,
    )

    postal_code = models.CharField(
        max_length=10,
        verbose_name=_('Postal code'),
        help_text=_('Postal code'),
        blank=True,
    )

    country = models.ForeignKey(
        Country,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_('Country'),
        help_text=_('Location country'),
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
        


# class SupplierPart(models.Model):
#     """
#     Represents a unique part provided by a Supplier.

#     Each SupplierPart is identified by a SKU (Supplier Part Number) and is linked to a Part or ManufacturerPart object.
#     A Part may be available from multiple suppliers.

#     Attributes:
#         - part (Part): Link to the master Part (Obsolete).
#         - source_item (SourcingItem): The sourcing item linked to this SupplierPart instance.
#         - supplier (Company): Company that supplies this SupplierPart object.
#         - SKU (str): Stock keeping unit (supplier part number).
#         - manufacturer_part (ManufacturerPart): Link to the associated ManufacturerPart (optional).
#         - link (str): Link to external website for this supplier part.
#         - description (str): Descriptive notes field for the supplier part.
#         - note (str): Longer form note field.
#         - base_cost (Decimal): Base charge added to order independent of quantity, e.g., "Reeling Fee".
#         - packaging (str): Packaging that the part is supplied in, e.g., "Reel".
#         - pack_quantity (str): Quantity of item supplied in a single pack (e.g., 30ml in a single tube).
#         - pack_quantity_native (Decimal): Pack quantity, converted to "native" units of the referenced part.
#         - multiple (PositiveIntegerField): Order multiple.
#         - available (Decimal): Quantity available from the supplier.
#         - availability_updated (DateTimeField): Date of the last update of availability data.
#     """

#     class Meta:
#         """Metaclass defines extra model options."""
#         unique_together = ('part', 'supplier', 'SKU')
#         db_table = 'part_supplierpart'


#     part = models.ForeignKey(
#         'part.Part',
#         on_delete=models.CASCADE,
#         related_name='supplier_parts',
#         verbose_name=_('Base Part'),
#         limit_choices_to={'purchaseable': True},
#         help_text=_('Select part'),
#     )

#     supplier = models.ForeignKey(
#         Company,
#         on_delete=models.CASCADE,
#         related_name='supplied_parts',
#         limit_choices_to={'is_supplier': True},
#         verbose_name=_('Supplier'),
#         help_text=_('Select supplier'),
#     )

#     SKU = models.CharField(
#         max_length=100,
#         verbose_name=_('SKU = Stock Keeping Unit (supplier part number)'),
#         help_text=_('Supplier stock keeping unit'),
#     )


#     link = models.URLField(
#         blank=True,
#         null=True,
#         verbose_name=_('Link'),
#         help_text=_('URL for external supplier part link'),
#     )

#     description = models.CharField(
#         max_length=250,
#         blank=True,
#         null=True,
#         verbose_name=_('Description'),
#         help_text=_('Supplier part description'),
#     )

#     note = models.CharField(
#         max_length=100,
#         blank=True,
#         null=True,
#         verbose_name=_('Note'),
#         help_text=_('Notes'),
#     )

#     base_cost = models.DecimalField(
#         max_digits=10,
#         decimal_places=3,
#         default=0,
#         validators=[MinValueValidator(0)],
#         verbose_name=_('Base cost'),
#         help_text=_('Minimum charge, e.g., stocking fee'),
#     )

#     packaging = models.CharField(
#         max_length=50,
#         blank=True,
#         null=True,
#         verbose_name=_('Packaging'),
#         help_text=_('Part packaging'),
#     )

#     pack_quantity = models.CharField(
#         max_length=25,
#         verbose_name=_('Pack Quantity'),
#         help_text=_(
#             'Total quantity supplied in a single pack. Leave empty for single items.'
#         ),
#         blank=True,
#         null=True,

#     )

#     pack_quantity_native = models.DecimalField(
#         max_digits=20,
#           decimal_places=10, 
#           default=1, 
#           blank=True,
#           null=True
#     )

#     def base_quantity(self, quantity=1) -> Decimal:
#         """Calculate the base unit quantity for a given quantity."""
#         q = Decimal(quantity) * Decimal(self.pack_quantity_native)
#         q = round(q, 10).normalize()
#         return q

#     multiple = models.PositiveIntegerField(
#         default=1,
#         validators=[MinValueValidator(1)],
#         verbose_name=_('Order multiple'),
#         help_text=_('Order multiple'),
#     )

#     available = models.DecimalField(
#         max_digits=10,
#         decimal_places=3,
#         default=0,
#         validators=[MinValueValidator(0)],
#         verbose_name=_('Available'),
#         help_text=_('Quantity available from supplier'),
#     )

#     availability_updated = models.DateTimeField(
#         null=True,
#         blank=True,
#         verbose_name=_('Availability Updated'),
#         help_text=_('Date of last update of availability data'),
#     )


# class SupplierPriceBreak(models.Model):
#     """
#     Represents a quantity price break for a SupplierPart.

#     - Suppliers can offer discounts at larger quantities
#     - SupplierPart(s) may have zero-or-more associated SupplierPriceBreak(s)

#     - Attributes:
#         - part (SupplierPart): Link to a SupplierPart object that this price break applies to.
#         - updated (DateTime): Automatic DateTime field that shows the last time the price break was updated.
#         - quantity (PositiveIntegerField): Quantity required for the price break.
#         - cost (Decimal): Cost at the specified quantity.
#         - currency (str): Reference to the currency of this price break (leave empty for the base currency).
#     """

#     class Meta:
#         """Metaclass defines extra model options."""
#         unique_together = ('part', 'quantity')
#         db_table = 'part_supplierpricebreak'

#     part = models.ForeignKey(
#         SupplierPart,
#         on_delete=models.CASCADE,
#         related_name='price_breaks',
#         verbose_name=_('Supplier Part'),
#         help_text=_('Select supplier part'),
#     )

#     updated = models.DateTimeField(auto_now=True, verbose_name=_('Updated'))

#     quantity = models.PositiveIntegerField(
#         verbose_name=_('Quantity'),
#         help_text=_('Quantity required for the price break'),
#     )

#     cost = models.DecimalField(
#         max_digits=10,
#         decimal_places=3,
#         verbose_name=_('Cost'),
#         help_text=_('Cost at the specified quantity'),
#     )



#     currency = models.CharField(
#         default=DEFAULT_CURRENCY_CODE,
#         blank=True,
#         max_length=12,
#         verbose_name=_('Currency'),
#         help_text=_('Reference to the currency of this price break (leave empty for base currency)'),
#         # validators=[validate_currency_code],
#         choices=currency_code_mappings,
#     )

registerable_models=[Address,Contact,Company]
