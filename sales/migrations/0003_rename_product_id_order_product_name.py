# Generated by Django 3.2.15 on 2022-10-08 13:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0002_auto_20221008_2145'),
    ]

    operations = [
        migrations.RenameField(
            model_name='order',
            old_name='product_id',
            new_name='product_name',
        ),
    ]
