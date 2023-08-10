# Generated by Django 4.2 on 2023-08-08 17:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="categoryimage",
            name="category",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="image",
                to="api.category",
            ),
        ),
    ]
