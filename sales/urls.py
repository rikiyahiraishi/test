from django.urls import path, include

#from sales.forms import ProductSearchForm
from . import views

app_name = 'sales'


urlpatterns = [
    # 初期表示画面
    path('', views.Index.as_view(), name='index'),

    # 商品情報関連画面
    path('product', views.ProductList.as_view(), name='product_list'),
    path('product_create/', views.ProductCreate.as_view(), name='product_create'),
    path('product_update/<int:pk>/', views.ProductUpdate.as_view(), name='product_update'), 
    path('product_delete/<int:pk>/', views.ProductDelete.as_view(), name='product_delete'),
    path('product_search/', views.ProductSearch, name='product_search'),
    path('product_download/', views.ProductDowmload, name='product_download'),

    # 顧客情報関連画面
    path('customer', views.CustomerList.as_view(), name='customer_list'),
    path('customer_create/', views.CustomerCreate.as_view(), name='customer_create'),
    path('customer_update/<int:pk>/', views.CustomerUpdate.as_view(), name='customer_update'), 
    path('customer_delete/<int:pk>/', views.CustomerDelete.as_view(), name='customer_delete'),
    path('customer_search/', views.CustomerSearch, name='customer_search'),
    path('customer_download/', views.CustomerDowmload, name='customer_download'),

    # 受入情報関連画面
    path('order', views.order_list, name='order_list'),
    path('order_customer_set', views.order_customer_set, name='order_customer_set'),
    path('order_create/', views.order_create, name='order_create'),
    path('order_update/<int:pk>/', views.order_update, name='order_update'), 
    path('order_delete/<int:pk>/', views.order_delete, name='order_delete'),
    path('order_search/', views.OrderSearch, name='order_search'),

    # 納品書作成関連画面
    path('delivery_slip', views.delivery_slip, name='delivery_slip'),
    #path('delivery_customer_set', views.delivery_customer_set, name='delivery_customer_set'),
    path('delivery_search', views.delivery_search, name='delivery_search'),
    path('create_delivery_slip', views.create_delivery_slip, name='create_delivery_slip'),

    # 請求書作成関連画面
    path('invoice_slip', views.invoice_slip, name='invoice_slip'),
    path('invoice_search', views.invoice_search, name='invoice_search'),
    path('create_invoice_slip', views.create_invoice_slip, name='create_invoice_slip'),
]
