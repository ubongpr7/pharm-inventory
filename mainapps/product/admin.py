from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline

from mainapps.common.models import Attachment
from mainapps.product.models import ProductVariant

class AttachmentInline(GenericTabularInline):
    model = Attachment
    extra = 1
    fields = ('file', 'purpose', 'is_primary', 'description')
    ct_field = 'content_type'
    ct_fk_field = 'object_id'

@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    inlines = [AttachmentInline]
    list_display = ('sku', 'product', )