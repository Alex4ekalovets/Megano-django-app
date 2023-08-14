# Generated by Django 4.2 on 2023-08-10 19:05

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("api", "0005_product_limited_edition"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="categoryimage",
            options={
                "verbose_name": "category image",
                "verbose_name_plural": "categories images",
            },
        ),
        migrations.AlterModelOptions(
            name="productimage",
            options={
                "ordering": ["src"],
                "verbose_name": "product image",
                "verbose_name_plural": "products images",
            },
        ),
        migrations.AlterModelOptions(
            name="producttag",
            options={
                "verbose_name": "product tag",
                "verbose_name_plural": "products tags",
            },
        ),
        migrations.AlterModelOptions(
            name="profile",
            options={"verbose_name": "profile", "verbose_name_plural": "profiles"},
        ),
        migrations.AlterModelOptions(
            name="profileavatar",
            options={
                "verbose_name": "profile avatar",
                "verbose_name_plural": "profiles avatars",
            },
        ),
        migrations.CreateModel(
            name="Sale",
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
                    "salePrice",
                    models.DecimalField(
                        decimal_places=2,
                        default=0,
                        max_digits=8,
                        verbose_name="Sale price",
                    ),
                ),
                ("dateFrom", models.DateTimeField(verbose_name="Sale start")),
                ("dateTo", models.DateTimeField(verbose_name="Sale end")),
                (
                    "product",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="sale",
                        to="api.product",
                        verbose_name="Product",
                    ),
                ),
            ],
            options={
                "verbose_name": "sale",
                "verbose_name_plural": "sales",
            },
        ),
    ]
