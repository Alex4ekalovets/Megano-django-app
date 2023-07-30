# Generated by Django 4.2.3 on 2023-07-27 16:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("shopapp", "0006_alter_review_product"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="product",
            options={"verbose_name": "product", "verbose_name_plural": "products"},
        ),
        migrations.AlterModelOptions(
            name="review",
            options={"verbose_name": "review", "verbose_name_plural": "reviews"},
        ),
        migrations.AlterModelOptions(
            name="tag",
            options={"verbose_name": "tag", "verbose_name_plural": "tags"},
        ),
        migrations.CreateModel(
            name="Specification",
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
                ("name", models.CharField(max_length=100)),
                ("value", models.CharField(max_length=200)),
                (
                    "product",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="specifications",
                        to="shopapp.product",
                    ),
                ),
            ],
            options={
                "verbose_name": "specification",
                "verbose_name_plural": "Specifications",
            },
        ),
    ]
