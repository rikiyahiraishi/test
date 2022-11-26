from ctypes import addressof
from multiprocessing import managers
from django.db import models

# bootstrapのテーマカラー
COLOR_CHOICES = (('primary', 'primary'),
                 ('secondary', 'secondary'),
                 ('success', 'success'),
                 ('info', 'info'),
                 ('warning', 'warning'),
                 ('danger', 'danger'),
                 ('light', 'light'),
                 ('dark', 'dark'))


class Products(models.Model):
    name = models.CharField('商品名', max_length=50, unique=True)
    unit_price = models.CharField('単価', max_length=50)
    unit = models.CharField('単位', max_length=50)

    def __str__(self):
        return self.name


class Customer(models.Model):
    customer_name = models.CharField('顧客様名', max_length=50, unique=True)
    post_code = models.CharField('郵便番号', max_length=10)
    address = models.CharField('住所', max_length=50)
    phone_number = models.CharField('電話番号', max_length=15, blank=True, null=True)
    manager = models.CharField('担当者', max_length=20, blank=True, null=True)

    def __str__(self):
        return self.customer_name


class Order(models.Model):
    order_datetime = models.DateTimeField('受注日時', auto_now_add=True)
    product_name = models.CharField('商品名', max_length=50)
    unit_price = models.CharField('単価', max_length=50)
    unit = models.CharField('単位', max_length=50)
    volume = models.FloatField('数量')
    total_price = models.IntegerField('合計')
    customer_name = models.CharField('顧客名', max_length=50)
    # 納品日として使用
    delivery_date = models.DateField('納品日', blank=True, null=True)
    delivery_status = models.BooleanField('納品')
    #delivery_date = models.DateField('納品日', blank=True, null=True)
    delivery_number = models.CharField('納品番号', blank=True, null=True, max_length=50)
    invoice_status = models.BooleanField('請求')
    invoice_number = models.CharField('請求番号', blank=True, null=True, max_length=50)
    invoice_date = models.DateField('請求日', blank=True, null=True)

    def __float__(self):
        return self.volume
