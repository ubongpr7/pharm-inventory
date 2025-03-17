from decimal import Decimal
import requests
from django.db import models

from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _
from django.utils.crypto import get_random_string
from django.utils.text import slugify
from mptt.models import MPTTModel, TreeForeignKey

from mainapps.inventory import InventoryMixin



def get_conversion_rate(currency):

    base_currency = 'USD'  

    api_url = f'https://api.exchangerate-api.com/v4/latest/{base_currency}'



    try:

        response = requests.get(api_url)

        response.raise_for_status()  

        data = response.json()

        conversion_rates = data['rates']



        if currency in conversion_rates:

            return conversion_rates[currency]

        else:

            raise ValueError('Invalid currency')

    

    except requests.exceptions.RequestException as e:

        raise ValueError('Failed to retrieve conversion rate') from e


class Category(MPTTModel):

    name = models.CharField(max_length=200, unique=True, help_text='It must be unique', verbose_name='Category')

    slug = models.SlugField(max_length=230, editable=False)

    is_active = models.BooleanField(default=True)

    parent = TreeForeignKey(

        "self",

        on_delete=models.PROTECT,

        related_name="children",

        null=True,

        blank=True

    )



    class MPTTMeta:

        order_insertion_by = ["name"]



    class Meta:

        ordering = ["name"]

        verbose_name_plural = _("categories")



    def save(self, *args, **kwargs):

        self.slug = slugify(self.name)

        super(Category, self).save(*args, **kwargs)



    def __str__(self):

        return self.name


class ProductType(MPTTModel):

    """

    CRUDable by only admins

    """

    name = models.CharField(max_length=255, unique=True)

    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)


    parent = TreeForeignKey("self",on_delete=models.PROTECT, related_name="children",null=True,  blank=True)
    def __str__(self):

        return self.name


class Product(InventoryMixin):

	name = models.CharField(max_length=230)

	slug = models.SlugField(max_length=255, editable=False)

	currency =models.CharField(max_length=5, default='USD')

	display_price = models.DecimalField(max_digits=12,null=True, blank=True, decimal_places=2,verbose_name='Display price ', validators=[MinValueValidator(Decimal("0.01"))])

	price_usd = models.DecimalField(max_digits=12,null=True, blank=True, decimal_places=2,verbose_name='Price in USD', validators=[MinValueValidator(Decimal("0.01"))])

	set_price_global=models.BooleanField(default=False, help_text='select if all product have the same price ')

	minimum_quantity= models.IntegerField(default=1)

	discount_available=models.BooleanField(default=False, help_text='Will there be discounts for bulk purchase')

	description = models.TextField(blank=True,help_text='Write full and general description of the product')

	category = models.ForeignKey(Category, related_name="products", on_delete=models.SET_NULL, null=True, blank=True)

	is_active = models.BooleanField(default=False,verbose_name='Available', )

	created_at = models.DateTimeField(auto_now_add=True,editable=False)

	updated_at = models.DateTimeField(auto_now=True)

    

	def save(self, *args, **kwargs):

		self.slug = slugify(self.name)

		if self.currency != 'USD':

			conversion_rate = get_conversion_rate(self.currency)

			self.price_usd = Decimal(self.display_price) / Decimal(conversion_rate)

		else:

			self.price_usd = self.display_price            

			super(Product, self).save(*args, **kwargs)


	def __str__(self):
		return self.name


class Brand(models.Model):

    name = models.CharField(max_length=255, unique=True)

    def __str__(self):

        return self.name


class ProductInventory(models.Model):

    brand = models.ForeignKey(Brand,verbose_name='Product manufactorer or Brand', on_delete=models.SET_NULL, blank=True, null=True, related_name="products")#to be saved as an instance

    is_active = models.BooleanField(default=False,verbose_name='Available')

    is_default = models.BooleanField(default=False,verbose_name='Set as default Product to be displayed')

    retail_price = models.DecimalField(max_digits=12, decimal_places=2,verbose_name='Selling  price', validators=[MinValueValidator(Decimal("0.01"))])

    store_price = models.DecimalField(max_digits=12, decimal_places=2,verbose_name='Cost price')

    updated_at = models.DateTimeField(auto_now=True)



    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="inventories")



    product_type = models.ForeignKey(ProductType, on_delete=models.PROTECT, related_name="inventories")# user will have choose based on the category of of product

    

    # non editatable

    created_at = models.DateTimeField(auto_now_add=True)

    sku = models.CharField(max_length=20, unique=True, editable=False)

    upc = models.CharField(max_length=12, unique=True, editable=False)

    generate_sku = models.BooleanField(default=True,editable=False, help_text='Autogenerate stock keeping unit')

    generate_upc = models.BooleanField(default=True, editable=False)

    class Meta:

        verbose_name_plural='Product Inventories'

    def save(self, *args, **kwargs):

        if self.generate_sku and not self.sku:

            self.sku = self.generate_sku_logic()

        if self.generate_upc and not self.upc:

            self.upc = self.generate_upc_logic()

        super(ProductInventory, self).save(*args, **kwargs)



    def generate_sku_logic(self):

        brand_initials = self.brand.name[:3].upper() if self.brand else "UNK"

        random_string = get_random_string(length=5)

        return f"{brand_initials}-{random_string}"



    def generate_upc_logic(self):

        brand_initials = self.brand.name[:3].upper() if self.brand else "000"

        random_string = get_random_string(length=9, allowed_chars='0123456789')

        return f"{brand_initials}{random_string}"


class Stock(models.Model):

    product_inventory = models.OneToOneField(ProductInventory, on_delete=models.PROTECT, related_name="stock")

    last_checked = models.DateTimeField(null=True, blank=True)

    units = models.IntegerField(default=0)

    units_sold = models.IntegerField(default=0)


class MinimumQuantity(models.Model):

    """

    we can add as many minimum with different discounts

    """

    quantity = models.PositiveIntegerField(default=1, help_text='Minimum quantity that will go for a certain amount')

    percentage_discount_on_price = models.DecimalField(max_digits=5, decimal_places=2, validators=[MinValueValidator(Decimal("0.01"))])

    product_inventory = models.ForeignKey(ProductInventory, on_delete=models.CASCADE, related_name='minimum_quantities')



    def __str__(self):

        return f"Minimum Quantity: {self.quantity}, Price per piece: {self.percentage_discount_on_price}"

    class Meta:

        verbose_name_plural='Minimum Quantities'
