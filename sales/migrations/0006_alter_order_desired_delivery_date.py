# Generated by Django 3.2.15 on 2022-10-23 03:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0005_remove_order_delivery_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='desired_delivery_date',
            field=models.DateField(blank=True, null=True, verbose_name='納品日'),
        ),
    ]
