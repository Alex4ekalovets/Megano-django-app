# Generated by Django 4.2.3 on 2023-07-27 13:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("shopapp", "0001_initial"),
    ]

    operations = [
        migrations.RenameField(
            model_name="productimage",
            old_name="description",
            new_name="alt",
        ),
        migrations.RenameField(
            model_name="productimage",
            old_name="image",
            new_name="src",
        ),
    ]