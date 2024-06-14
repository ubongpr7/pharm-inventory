from django.db import models
from django.utils.translation import gettext_lazy as _
from cities_light.models import Country, Region, SubRegion,City

from mptt.models import MPTTModel, TreeForeignKey
from django.utils.crypto import get_random_string
from django.utils.text import slugify
from django.conf import settings
from django_countries.fields import CountryField
from mainapps.common.validators import validate_city, validate_city_belongs_to_sub_region, validate_country, validate_postal_code, validate_region, validate_region_belongs_to_country, validate_sub_region
from mainapps.content_type_linking_models.models import GenericModel
User= settings.AUTH_USER_MODEL


class ModelChoice(models.TextChoices):
    inventory='inventory','Inventory'
    stockitem='stock_item',"Stock item"
    company='company',"Company"
    policy='policy',"Policy"
    industry='industry',"Industry"

class TypeOf(MPTTModel):

    name = models.CharField(
        max_length=200, 
        # unique=True, 
        help_text='It must be unique', 
        verbose_name='Type'
    )
    which_model=models.CharField(max_length=30,choices=ModelChoice.choices,)
    slug = models.SlugField(max_length=230, editable=False,)
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

        verbose_name_plural = _("Types of Instances")
        constraints=[
            models.UniqueConstraint(
                fields=[
                    'name',
                    'which_model'
                ],
                name='unique_type_name_which_model'
            )
        ]




    def save(self, *args, **kwargs):

        self.slug = f"{get_random_string(6)}{slugify(self.name)}-{self.pk}-{get_random_string(5)}"

        super(TypeOf, self).save(*args, **kwargs)


    def __str__(self):

        return self.name



class Address(models.Model):

    class Meta:
        abstract= True

    
    country = models.ForeignKey(
        Country, 
        on_delete=models.CASCADE,
        verbose_name=_('Country'),
        null=True,
    )
    region = models.ForeignKey(
        Region, 
        on_delete=models.CASCADE,
        verbose_name=_('Region/State'),
        null=True,
    )
    subregion = models.ForeignKey(
        SubRegion, 
        on_delete=models.CASCADE,
        verbose_name=_('Sub region/LGA'),
        null=True,
    )
    city = models.ForeignKey(
        City,
        on_delete=models.CASCADE,
        verbose_name=_('City/Town'),
        null=True,
     )
    apt_number = models.PositiveIntegerField(
        verbose_name=_('Apartment number'),
        null=True,
        blank=True
    )
    street_number = models.PositiveIntegerField(
        verbose_name=_('Street number'),
        null=True,
        blank=True
    )
    street = models.CharField(max_length=255,blank=False,null=True)

    postal_code = models.CharField(
        max_length=10,
        verbose_name=_('Postal code'),
        help_text=_('Postal code'),
        blank=True,
        null=True,
        validators=[validate_postal_code]
    )

    def __str__(self):
        return f'{self.street}, {self.city}, {self.region}, {self.country}'
    def clean(self):
        validate_country(self.country.id)
        validate_region(self.region.id)
        validate_sub_region(self.subregion.id)
        validate_city(self.city.id)
        validate_region_belongs_to_country(self.region.id, self.country.id)
        validate_city_belongs_to_sub_region(self.city.id, self.subregion.id)




class Attribute(models.Model):
    name = models.CharField(max_length=255)

class Value(models.Model):
    attribute = models.ForeignKey(Attribute, on_delete=models.CASCADE)
    value = models.CharField(max_length=255)
    class Meta:
        unique_together = ('attribute', 'value')
class Unit(models.Model):
    attribute = models.ForeignKey(Attribute, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)

class AttributeStore(GenericModel):
    attributes= models.JSONField(default=dict)


registerable_models=[Attribute,Value,Unit,AttributeStore,TypeOf]

