# Generated by Django 3.2.15 on 2022-10-23 03:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0004_auto_20221011_2248'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='delivery_date',
        ),
    ]
