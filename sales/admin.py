from django.contrib import admin
from .models import Customer, Order, Products


@admin.register(Products)
class ProductsAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'unit_price', 'unit', 'user', )
    list_display_links = ('name',)
    #ordering = ('unit_price',)

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer_name', 'post_code', 'address', 'phone_number', 'manager', 'user', )
    list_display_links = ('customer_name',)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'order_datetime', 'product_name', 'volume', 'total_price', 'customer_name', 'delivery_date', 'delivery_status', 'delivery_number', 'invoice_status', 'invoice_number', 'invoice_date', 'user', )
    list_display_links = ('order_datetime',)
