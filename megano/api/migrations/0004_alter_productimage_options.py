# Generated by Django 4.2 on 2023-08-09 17:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0003_alter_productimage_options_alter_category_parent_and_more"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="productimage",
            options={"ordering": ["src"]},
        ),
    ]