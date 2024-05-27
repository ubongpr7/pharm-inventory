from django.db import models
from django.utils.translation import gettext_lazy as _

from mptt.models import MPTTModel, TreeForeignKey
from django.utils.crypto import get_random_string
from django.utils.text import slugify
from django.conf import settings

from mainapps.content_type_linking_models.models import GenericModel
User= settings.AUTH_USER_MODEL






class Country(models.Model):
    country = models.CharField(max_length=30)
    # name = CountryField()
    class Meta:
        verbose_name_plural= _('Countries')
    def __str__(self):
        return self.name


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

def add_attribute(self, name, value, unit=None):
    """
    Add an attribute to the attributes field.

    Args:
        name (str): Attribute name.
        value: Attribute value.
        unit (str, optional): Attribute unit (e.g., 'kg', 'cm'). Defaults to None.
    """
    attribute = {'name': name, 'value': value, 'unit': unit}
    self.attributes.append(attribute)
    self.save()

class AttributeStore(GenericModel):
    attributes= models.JSONField(default=dict)


registerable_models=[Attribute,Value,Unit,Country,AttributeStore]

