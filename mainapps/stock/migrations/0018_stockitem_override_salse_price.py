# Generated by Django 5.2 on 2025-04-18 22:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0017_remove_saleitem_sale_remove_saleitem_stock_item_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='stockitem',
            name='override_salse_price',
            field=models.DecimalField(blank=True, decimal_places=2, help_text='Temporary price override for this stock batch', max_digits=10, null=True),
        ),
    ]
