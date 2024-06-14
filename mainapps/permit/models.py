from django.db import models


class CustomPermission(models.Model):
    """
    This is a permission that can be common to all models in the db
    """
    class Meta:
        managed=False #will not create data in db
        default_permissions=() # it will not allow default permissions such as view,create, delete, update
        permissions=(
            # add custom permissions here
            ('can_generate_report','Can generate report'),
            # ('can_download_report','Can download report'),
            # ('can_confirm_sales_order','Can confirm sales order'),
            # ('can_confirm_purchase_order','Can confirm purchase order'),
            # ('can_confirm_purchase_order','Can confirm purchase order'),
            # ('can_confirm_purchase_order','Can confirm purchase order'),

            # ('inventory_add_inventorycategory','Can create inventory category'),
            # ('inventory_view_inventorycategory','Can view inventory category '),
            # ('inventory_update_inventorycategory','Can update inventory category'),
            # ('inventory_delete_inventorycategory','Can delete inventory category'),
            
            # ('inventory_add_inventory','Can create inventory '),
            # ('inventory_view_inventory','Can view inventory  '),
            # ('inventory_update_inventory','Can update inventory '),
            # ('inventory_delete_inventory','Can delete inventory '),
            
            # ('inventory_add_inventory','Can create inventory category'),
            # ('inventory_view_inventory','Can view inventory category '),
            # ('inventory_update_inventory','Can update inventory category'),
            # ('inventory_delete_inventory','Can delete inventory category'),
            
            # ('can_confirm_purchase_order','Can confirm purchase order'),

        )