# Generated by Django 4.2 on 2023-08-15 17:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("api", "0008_remove_basket_count_remove_basket_product_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="Order",
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
                    "createdAt",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="Date of creation"
                    ),
                ),
                ("deliveryType", models.CharField(blank=True, max_length=128)),
                ("paymentType", models.CharField(blank=True, max_length=128)),
                ("status", models.CharField(blank=True, max_length=128)),
                ("city", models.CharField(blank=True, max_length=128)),
                ("address", models.CharField(blank=True, max_length=200)),
            ],
            options={
                "verbose_name": "Order",
                "verbose_name_plural": "Orders",
            },
        ),
        migrations.AlterModelOptions(
            name="basket",
            options={"verbose_name": "Basket", "verbose_name_plural": "Baskets"},
        ),
        migrations.AlterModelOptions(
            name="basketitem",
            options={
                "verbose_name": "Basket item",
                "verbose_name_plural": "Basket items",
            },
        ),
        migrations.AlterField(
            model_name="basketitem",
            name="count",
            field=models.IntegerField(default=1, verbose_name="Count"),
        ),
        migrations.CreateModel(
            name="OrderItem",
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
                ("count", models.IntegerField(default=1, verbose_name="Count")),
                (
                    "order",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="order_items",
                        to="api.order",
                        verbose_name="Order",
                    ),
                ),
                (
                    "product",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="order_items",
                        to="api.product",
                        verbose_name="Product",
                    ),
                ),
            ],
            options={
                "verbose_name": "Order item",
                "verbose_name_plural": "Order items",
            },
        ),
        migrations.AddField(
            model_name="order",
            name="products",
            field=models.ManyToManyField(
                related_name="orders",
                through="api.OrderItem",
                to="api.product",
                verbose_name="Products",
            ),
        ),
        migrations.AddField(
            model_name="order",
            name="profile",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="orders",
                to="api.profile",
                verbose_name="Profile",
            ),
        ),
    ]