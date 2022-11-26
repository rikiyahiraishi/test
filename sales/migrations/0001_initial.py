# Generated by Django 3.2.15 on 2022-10-07 14:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('customer_name', models.CharField(max_length=50, unique=True, verbose_name='顧客様名')),
                ('post_code', models.CharField(max_length=10, verbose_name='郵便番号')),
                ('address', models.CharField(max_length=50, verbose_name='住所')),
                ('phone_number', models.CharField(blank=True, max_length=15, null=True, verbose_name='電話番号')),
                ('manager', models.CharField(blank=True, max_length=20, null=True, verbose_name='担当者')),
            ],
        ),
        migrations.CreateModel(
            name='Products',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True, verbose_name='商品名')),
                ('unit_price', models.CharField(max_length=50, verbose_name='単価')),
                ('unit', models.CharField(max_length=50, verbose_name='単位')),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_datetime', models.DateTimeField(auto_now_add=True, verbose_name='受注日時')),
                ('product_id', models.CharField(max_length=50, verbose_name='商品名')),
                ('volume', models.FloatField(verbose_name='数量')),
                ('total_price', models.IntegerField(verbose_name='合計')),
                ('desired_delivery_date', models.DateField(blank=True, null=True, verbose_name='希望納品日')),
                ('delivery_status', models.BooleanField(verbose_name='納品')),
                ('delivery_date', models.DateField(blank=True, null=True, verbose_name='納品日')),
                ('delivery_number', models.CharField(blank=True, max_length=50, null=True, verbose_name='納品番号')),
                ('invoice_status', models.BooleanField(verbose_name='請求')),
                ('invoice_number', models.CharField(blank=True, max_length=50, null=True, verbose_name='請求番号')),
                ('invoice_date', models.DateField(blank=True, null=True, verbose_name='請求日')),
                ('customer_id', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='CustomerID', to='sales.customer')),
            ],
        ),
    ]
