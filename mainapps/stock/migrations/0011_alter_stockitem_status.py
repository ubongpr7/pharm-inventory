# Generated by Django 5.2 on 2025-04-07 00:23

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0010_sale_saleitem_stockpricing'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stockitem',
            name='status',
            field=models.CharField(choices=[('ok', 'OK'), ('attention_needed', 'Attention needed'), ('damaged', 'Damaged'), ('destroyed', 'Destroyed'), ('rejected', 'Rejected'), ('lost', 'Lost'), ('quarantined', 'Quarantined'), ('returned', 'Returned')], default='ok', help_text='Status of this StockItem ', max_length=50, validators=[django.core.validators.MinValueValidator(0)], verbose_name='Status'),
        ),
    ]
