from django.db import models


class CustomPermissionModel(models.Model):
    """
    This is a permission that can be common to all models in the db
    """
    class Meta:
        managed=False #will not create data in db
        default_permissions=() # it will not allow default permissions such as view,create, delete, update
        permissions=(
            # add custom permissions here
            ('can_generate_report','Can generate report'),
            ('can_download_report','Can download report'),
            ('can_confirm_sales_order','Can confirm sales order'),
            ('can_confirm_purchase_order','Can confirm purchase order'),

        )