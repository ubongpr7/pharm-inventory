# Generated by Django 5.1.7 on 2025-03-11 07:23

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("common", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="InventoryCategory",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        help_text="It must be unique",
                        max_length=200,
                        unique=True,
                        verbose_name="Category name*",
                    ),
                ),
                ("slug", models.SlugField(editable=False, max_length=230)),
                ("is_active", models.BooleanField(default=True)),
                ("description", models.TextField(blank=True, null=True)),
                ("lft", models.PositiveIntegerField(editable=False)),
                ("rght", models.PositiveIntegerField(editable=False)),
                ("tree_id", models.PositiveIntegerField(db_index=True, editable=False)),
                ("level", models.PositiveIntegerField(editable=False)),
            ],
            options={
                "verbose_name_plural": "categories",
                "ordering": ["name"],
            },
        ),
        migrations.CreateModel(
            name="Inventory",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "minimum_stock_level",
                    models.IntegerField(
                        default=0,
                        help_text="Minimum stock level before you receive alert",
                    ),
                ),
                (
                    "re_order_point",
                    models.IntegerField(
                        default=10,
                        help_text="At what point can reorder activities be triggered",
                    ),
                ),
                (
                    "automate_reorder",
                    models.BooleanField(
                        default=False,
                        help_text="If product reaches reorder point, do you want an automated reorder processing?",
                    ),
                ),
                ("re_order_quantity", models.IntegerField(default=200)),
                (
                    "recall_policy",
                    models.CharField(
                        choices=[
                            ("0", "Remove from stock"),
                            ("1", "Notify customers"),
                            ("3", "Replace item"),
                            ("4", "Destroy item"),
                            ("5", "Repair item"),
                        ],
                        default="0",
                        help_text="What happens if product is bad",
                        max_length=200,
                    ),
                ),
                (
                    "expiration_policy",
                    models.CharField(
                        choices=[
                            ("0", "Dispose of stock"),
                            ("1", "Return to manufacturer"),
                        ],
                        default="0",
                        help_text="What happens if product expires",
                        max_length=200,
                    ),
                ),
                (
                    "name",
                    models.CharField(max_length=255, verbose_name="Inventory name*"),
                ),
                ("description", models.TextField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "created_by",
                    models.ForeignKey(
                        editable=False,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="inventories",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "i_type",
                    models.ForeignKey(
                        limit_choices_to={"which_model": "inventory"},
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="common.typeof",
                        verbose_name="Type of  inventory*",
                    ),
                ),
            ],
            options={
                "verbose_name_plural": "Inventories",
                "ordering": ["-created_at"],
            },
        ),
    ]
