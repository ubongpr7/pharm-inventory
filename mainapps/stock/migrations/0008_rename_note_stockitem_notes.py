# Generated by Django 5.2 on 2025-04-06 14:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0007_stockitem_note'),
    ]

    operations = [
        migrations.RenameField(
            model_name='stockitem',
            old_name='note',
            new_name='notes',
        ),
    ]
