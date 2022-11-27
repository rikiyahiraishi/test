#from asyncio.windows_events import NULL
from audioop import reverse
from curses import A_ALTCHARSET
from encodings import search_function
from multiprocessing import context
from pyexpat import model
import re
from urllib import request
from django.shortcuts import render, resolve_url
from django.http import HttpResponse
from django.views.generic import TemplateView, CreateView, ListView, DeleteView, UpdateView
import numpy as np
from .models import Products, Customer, Order
from .forms import ProductCreateForm, ProductUpdateForm, ProductSearchForm, CustomerCreateForm, CustomerUpdateForm, CustomerSearchForm, OrderCreateForm, OrderUpdateForm, DeliveryFilterForm
from django.db.models import Q
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.contrib import messages
import urllib
import csv
from decimal import Decimal
from . import orig_parts
from django_pandas.io import read_frame
import pandas as pd
import numpy as np
import datetime
import calendar
import os



# 初期画面
class Index(TemplateView):
    model = Order
    template_name = 'sales/index.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)

        today = datetime.date.today()
        start = '{0}-01-01'.format(today.year)
        end = '{0}-12-31'.format(today.year)
        # 年間売上関連処理
        queryset = Order.objects.filter(delivery_status=True, delivery_date__gte=start, delivery_date__lte=end)
        #queryset = Order.objects.filter(delivery_status=True)
        df = read_frame(queryset, fieldnames=['customer_name', 'total_price', 'delivery_date'])
        # 年間売上の算出と総受入件数の算出
        context['total_sales'] = df['total_price'].sum()
        context['total_cnt'] = len(df)

        # グラフ作成のためのpivot集計
        df_pivot = pd.pivot_table(df, index='delivery_date', columns='customer_name', values='total_price', aggfunc=np.sum, fill_value=0)

        # X軸は月の情報、Y軸は売上額
        context['month_list'] = [month.strftime('%m/%d') for month in df_pivot.index.values]
        #context['sales_list'] = [[val[0] for val in df_pivot.values], [val[1] for val in df_pivot.values]]
        #print([val[0] for val in df_pivot.values])
        # 顧客毎の売上集計
        customer_sales = list()
        for i in range(len(df_pivot.columns.values)):
            customer_name = df_pivot.columns.values[i]

            total = 0
            sales_list = list()
            for t in df_pivot[customer_name].values:
                total = total + t
                sales_list.append(total)
            customer_sales.append(sales_list)
        context['sales_list'] = customer_sales

        # 顧客毎の年間売上金額
        customer_sales_dict = dict()
        df_pivot = pd.pivot_table(df, index='customer_name', values='total_price', aggfunc=np.sum, fill_value=0)
        for i in range(len(df_pivot.index.values)):
            customer_sales_dict[df_pivot.index.values[i]] = df_pivot.values[i][0]
        context['customer_sales_dict'] = customer_sales_dict

        # 未納品件数処理関連
        queryset = Order.objects.filter(delivery_status=False)
        df = read_frame(queryset, fieldnames=['customer_name', 'total_price', 'delivery_date'])
        # 未納品件数の算出
        context['undelivery_cnt'] = len(df)
        # 未納品商品がある顧客名とその件数を算出
        df_pivot = pd.pivot_table(df, index='customer_name', values='total_price', aggfunc=len, fill_value=0)

        undelivey_dict = dict()
        for i in range(len(df_pivot.index.values)):
            undelivey_dict[df_pivot.index.values[i]] = df_pivot.values[i][0]
        context['undelivey_dict'] = undelivey_dict

        # 月間売上関連処理
        start = '{0}-{1}-01'.format(today.year, today.month)
        _, lastday = calendar.monthrange(today.year, today.month)
        end = '{0}-{1}-{2}'.format(today.year, today.month, lastday)
        queryset = Order.objects.filter(delivery_status=True, delivery_date__gte=start, delivery_date__lte=end)
        df = read_frame(queryset, fieldnames=['customer_name', 'total_price'])
        context['month_sales'] = df['total_price'].sum()

        # 月間顧客別売上
        customer_monthsales_dict = dict()
        df_pivot = pd.pivot_table(df, index='customer_name', values='total_price', aggfunc=np.sum, fill_value=0)
        for i in range(len(df_pivot.index.values)):
            customer_monthsales_dict[df_pivot.index.values[i]] = df_pivot.values[i][0]
        context['customer_monthsales_dict'] = customer_monthsales_dict

        return context



#################################
# 商品情報のリスト表示
################################# 
class ProductList(ListView):
    model = Products
    paginate_by = 5

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['product_create_form'] = ProductCreateForm
        context['product_update_form'] = ProductUpdateForm
        return context

    def get_queryset(self):
        return Products.objects.all()



#################################
# 商品情報の新規登録
################################# 
class ProductCreate(CreateView):
    model = Products
    form_class = ProductCreateForm
    success_url = reverse_lazy('sales:product_list')

    def form_valid(self, form):
        # フォームから値を受け取る
        name = str(self.request.POST.get('name'))
        unit_price = str(self.request.POST.get('unit_price'))
        unit = str(self.request.POST.get('unit'))

        new_product = form.save(commit=False)
        new_product.target = Products
        new_product.save()

        message = "商品名「{0}」を新規登録しました。単価：{1}　単位：{2}".format(name, unit_price, unit)
        messages.add_message(self.request, messages.INFO, message)

        return redirect('sales:product_list')
    
    def form_invalid(self, form):
        error_message = form.errors.get_json_data()
        # エラーメッセージの種別確認
        if 'name' in error_message:
            messages.add_message(self.request, messages.ERROR, error_message['name'][0]['message'])
        else:
            messages.add_message(self.request, messages.ERROR, error_message['unit_price'][0]['message'])

        return redirect('sales:product_list')



#################################
# 商品情報の更新
################################# 
class ProductUpdate(UpdateView):
    model = Products
    template_name = 'sales/product_list.html'
    form_class = ProductUpdateForm

    def form_valid(self, form):
        name = str(self.request.POST.get('name'))
        unit_price = str(self.request.POST.get('unit_price'))
        unit = str(self.request.POST.get('unit'))

        message = "商品名「{0}」を更新しました。単価：{1}　単位：{2}".format(name, unit_price, unit)
        messages.add_message(self.request, messages.INFO, message)

        return super().form_valid(form)
    
    def get_success_url(self):
        #view_name = 'sales:product_list'
        #pk = self.object.pk
        return resolve_url('sales:product_list')

    def form_invalid(self, form):
        error_message = form.errors.get_json_data()
        messages.add_message(self.request, messages.ERROR, error_message['unit_price'][0]['message'])

        return redirect('sales:product_list')



#################################
# 商品情報の削除
################################# 
class ProductDelete(DeleteView):
    """商品情報の削除ビュー"""
    model = Products

    def get_success_url(self):
        data = self.get_context_data()
        message = "商品名「{0}」を削除しました。".format(data['object'])
        messages.add_message(self.request, messages.ERROR, message)

        return reverse_lazy('sales:product_list')



#################################
# 商品情報の検索
#################################  
def ProductSearch(request):
    searchform = ProductSearchForm(request.GET)

    if searchform.is_valid():
        freeword = searchform.cleaned_data['freeword']
    search_list = Products.objects.filter(Q(name__icontains = freeword)|Q(unit__icontains = freeword)|Q(unit_price__icontains = freeword))
    
    page_obj, next, prev = orig_parts.pagenation(request, search_list)

    params = {
        "product_create_form": ProductCreateForm,
        "product_update_form": ProductUpdateForm,
        'object_list': page_obj,
        'next_page_href': orig_parts.some_page_href(next, '', freeword),
        'prev_page_href': orig_parts.some_page_href(prev, '', freeword),
        'freeword': freeword
    }

    return render(request, 'sales/products_list.html', params)



#################################
# 商品情報のダウンロード
#################################
def ProductDowmload(request):
    response = HttpResponse(content_type='text/csv; charset=Shift-JIS')
    filename = urllib.parse.quote((u'商品情報.csv').encode("utf8"))
    response['Content-Disposition'] = 'attachment; filename*=UTF-8\'\'{}'.format(filename)
    header = ['ID', '商品名', '単価', '単位']

    # 商品情報の取得
    product_list = []
    table_obj = request.GET
    if request.GET['button_type'] == 'this_table':
        for t in table_obj:
            result_name = re.match('name_\d+', t)
            if result_name:
                id = result_name.group().split('_')[1]
                name = table_obj[t]
                unit_price = table_obj['unit_price_{0}'.format(id)]
                unit = table_obj['unit_{0}'.format(id)]
                product_list.append([id, name, unit_price, unit])
    else:
        object_list = Products.objects.all()
        for i in object_list:
            product_list.append([i.id, i.name, i.unit_price, i.unit])
    
    # CSVファイルの書き込み
    writer = csv.writer(response)
    writer.writerow(header) 
    for item in product_list:
        writer.writerow([item[0], item[1], item[2], item[3]])

    return response    



#################################
# 顧客情報のリスト表示
################################# 
class CustomerList(ListView):
    model = Customer
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['customer_create_form'] = CustomerCreateForm
        context['customer_update_form'] = CustomerUpdateForm
        return context

    def get_queryset(self):
        return Customer.objects.all()



#################################
# 顧客情報の登録
################################# 
class CustomerCreate(CreateView):
    """
    顧客情報の新規作成ビュー
    顧客管理ページのフォームからモデル保存処理をする
    """
    model = Customer
    form_class = CustomerCreateForm
    success_url = reverse_lazy('sales:customer_list')

    def form_valid(self, form):
        # フォームから値を受け取る
        customer_name = str(self.request.POST.get('customer_name'))
        post_code = str(self.request.POST.get('post_code'))
        address = str(self.request.POST.get('address'))
        phone_number = str(self.request.POST.get('phone_number'))
        manager = str(self.request.POST.get('manager'))

        new_customer = form.save(commit=False)
        new_customer.target = Products
        new_customer.save()

        message = "会社名「{0}」を新規登録しました。郵便番号：{1}　住所：{2}　電話番号：{3}　担当者：{4}".format(customer_name, post_code, address, phone_number, manager)
        messages.add_message(self.request, messages.INFO, message)

        return redirect('sales:customer_list')
    
    def form_invalid(self, form):
        error_message = form.errors.get_json_data()
        # エラーメッセージの種別確認
        if 'customer_name' in error_message:
            messages.add_message(self.request, messages.ERROR, error_message['customer_name'][0]['message'])
        else:
            pass

        return redirect('sales:product_list')



#################################
# 顧客情報の更新 
################################# 
class CustomerUpdate(UpdateView):
    model = Customer
    template_name = 'sales/customer_list.html'
    form_class = CustomerUpdateForm

    def form_valid(self, form):
        customer_name = str(self.request.POST.get('customer_name'))
        post_code = str(self.request.POST.get('post_code'))
        address = str(self.request.POST.get('address'))
        phone_number = str(self.request.POST.get('phone_number'))
        manager = str(self.request.POST.get('manager'))

        message = "会社名「{0}」を更新しました。郵便番号：{1}　住所：{2}　電話番号：{3}　担当者：{4}".format(customer_name, post_code, address, phone_number, manager)
        messages.add_message(self.request, messages.INFO, message)

        return super().form_valid(form)
    
    def get_success_url(self):
        return resolve_url('sales:customer_list')

    def form_invalid(self, form):
        error_message = form.errors.get_json_data()
        messages.add_message(self.request, messages.ERROR, error_message['unit_price'][0]['message'])

        return redirect('sales:customer_list')



#################################
# 顧客情報の削除
################################# 
class CustomerDelete(DeleteView):
    """商品情報の削除ビュー"""
    model = Customer

    def get_success_url(self):
        data = self.get_context_data()
        message = "商品名「{0}」を削除しました。".format(data['object'])
        messages.add_message(self.request, messages.ERROR, message)

        return reverse_lazy('sales:customer_list')



#################################
# 顧客情報の検索 
#################################    
def CustomerSearch(request):
    #if request.method == 'POST':
    searchform = CustomerSearchForm(request.GET)

    if searchform.is_valid():
        freeword = searchform.cleaned_data['freeword']
    search_list = Customer.objects.filter(Q(customer_name__icontains = freeword)|Q(post_code__icontains = freeword)|Q(address__icontains = freeword)|Q(phone_number__icontains = freeword)|Q(manager__icontains = freeword))

    page_obj, next, prev = orig_parts.pagenation(request, search_list)

    params = {
        "customer_create_form": CustomerCreateForm,
        "customer_update_form": CustomerUpdateForm,
        "customer_search_form": searchform,
        'object_list': page_obj,
        'next_page_href': orig_parts.some_page_href(next, '', freeword),
        'prev_page_href': orig_parts.some_page_href(prev, '', freeword),
        'freeword': freeword
    }

    return render(request, 'sales/customer_list.html', params)



#################################
# 顧客情報のダウンロード
#################################
def CustomerDowmload(request):
    response = HttpResponse(content_type='text/csv; charset=Shift-JIS')
    filename = urllib.parse.quote((u'会社情報.csv').encode("utf8"))
    response['Content-Disposition'] = 'attachment; filename*=UTF-8\'\'{}'.format(filename)
    header = ['ID', '会社名', '郵便番号', '住所', '電話番号', '担当者']

    # 顧客情報の取得
    customer_list = []
    table_obj = request.GET
    if request.GET['button_type'] == 'this_table':
        for t in table_obj:
            result_customer_name = re.match('customer_name_\d+', t)
            if result_customer_name:
                id = result_customer_name.group().split('_')[2]
                customer_name = table_obj[t]
                post_code = table_obj['post_code_{0}'.format(id)]
                address = table_obj['address_{0}'.format(id)]
                phone_number = table_obj['phone_number_{0}'.format(id)]
                manager = table_obj['manager_{0}'.format(id)]
                customer_list.append([id, customer_name, post_code, address, phone_number, manager])
    else:
        object_list = Customer.objects.all()
        for i in object_list:
            customer_list.append([i.id, i.customer_name, i.post_code, i.address, i.phone_number, i.manager])
    
    # CSVファイルの書き込み
    writer = csv.writer(response)
    writer.writerow(header) 
    for item in customer_list:
        writer.writerow([item[0], item[1], item[2], item[3], item[4], item[5]])

    return response



#################################
# 受入情報リストの表示関連
#################################
def order_list(request):
    obj_list = Order.objects.all().order_by('-order_datetime')

    # 顧客名のドロップボックスを作成
    order_form = DeliveryFilterForm(request.GET)
    order_form = orig_parts.customer_dropbox(order_form)
    # ページネーション機能
    page_obj, next, prev = orig_parts.pagenation(request, obj_list)

    params = {
        'order_search_form': order_form,
        'order_create_form': OrderCreateForm(),
        'order_update_form': OrderUpdateForm(),
        'object_list': page_obj,
        'next_page_href': orig_parts.some_page_href(next, ''),
        'prev_page_href': orig_parts.some_page_href(prev, ''),
        'customer_name': ''
    }
    
    return render(request, 'sales/order_list.html', params)



#################################
# 受入画面での顧客セット
#################################
def order_customer_set(request):
    customer_name = request.GET.get('customer_name')
    if customer_name == '顧客名を選択してください':
        message = '顧客名を選択してください。'
        messages.add_message(request, messages.ERROR, message)
        return redirect('sales:order_list')

    # 商品名のドロップボックスを作成
    order_form = OrderCreateForm()
    order_form = orig_parts.products_dropbox(order_form)
    # 顧客名のドロップボックスを作成
    order_form2 = DeliveryFilterForm({'customer_name': customer_name})
    order_form2 = orig_parts.customer_dropbox(order_form2)
    # ページネーション機能
    obj_list = Order.objects.filter(customer_name=customer_name).order_by('-order_datetime')
    page_obj, next, prev = orig_parts.pagenation(request, obj_list)

    params = {
        'order_search_form': order_form2,
        'order_create_form': order_form,
        'order_update_form': OrderUpdateForm(),
        'object_list': page_obj,
        'next_page_href': orig_parts.some_page_href(next, customer_name),
        'prev_page_href': orig_parts.some_page_href(prev, customer_name),
        'customer_name': customer_name
    }

    return render(request, 'sales/order_list.html', params)



#################################
# 受入情報の新規作成
#################################
def order_create(request):
    if request.method == 'POST':
        customer_name = str(request.POST['customer_name'])
        product_element = str(request.POST.get('product_name'))
        product_name = product_element.split(':')[0]
        delivery_date = str(request.POST.get('delivery_date'))

        # volumeのバリデーション
        try:
            volume = Decimal(str(request.POST.get('volume')))
        except:
            message = "数量はカンマを含まない数値で入力してください。入力値：{0}".format(str(request.POST.get('volume')))
            messages.add_message(request, messages.ERROR, message)

            # 商品名のドロップボックスを作成
            order_form = OrderCreateForm()
            order_form = orig_parts.products_dropbox(order_form)
            # 顧客名のドロップボックスを作成
            order_form2 = DeliveryFilterForm({'customer_name': customer_name})
            order_form2 = orig_parts.customer_dropbox(order_form2)
            # ページネーション機能
            obj_list = Order.objects.filter(customer_name=customer_name).order_by('-order_datetime')
            page_obj, next, prev = orig_parts.pagenation(request, obj_list)

            params = {
                'order_search_form': order_form2,
                'order_create_form': order_form,
                'order_update_form': OrderUpdateForm(),
                'object_list': page_obj,
                'next_page_href': orig_parts.some_page_href(next, customer_name),
                'prev_page_href': orig_parts.some_page_href(prev, customer_name),
                'customer_name': customer_name
            }

            return render(request, 'sales/order_list.html', params)

        # 商品情報の取得と金額計算
        product_info = Products.objects.filter(name=product_name).values()[0]
        unit_price = Decimal(product_info['unit_price'])
        unit = product_info['unit']

        # 合計金額の計算([0]:数字、[1]:単位)
        spl = re.match('^(\d{1,10})(.)', unit)
        if spl:
            total_price = volume*(unit_price/Decimal(spl[1]))
        else:
            total_price = volume*unit_price

        # 受入情報の新規登録処理
        if delivery_date:
            Order.objects.create(customer_name=customer_name, product_name=product_name, unit_price=unit_price, unit=unit, volume=volume, total_price=total_price, delivery_date=delivery_date, delivery_status=False, invoice_status=False)
        else:
            Order.objects.create(customer_name=customer_name, product_name=product_name, unit_price=unit_price, unit=unit, volume=volume, total_price=total_price, delivery_status=False, invoice_status=False)
            delivery_date = '指定なし'

        # 更新処理完了後の表示情報のセット
        message = "受注情報を新規登録しました。顧客名：{0}　商品名：{1}　価格：{2}/{3}　数量：{4}　合計：{5}　納品日：{6}".format(
            customer_name, product_name, unit_price, unit ,volume, total_price, delivery_date
            )
        messages.add_message(request, messages.INFO, message)
    else:
        customer_name = str(request.GET['customer_name'])
    
    # 商品名のドロップボックスを作成
    order_form = OrderCreateForm()
    order_form = orig_parts.products_dropbox(order_form)
    # 顧客名のドロップボックスを作成
    order_form2 = DeliveryFilterForm({'customer_name': customer_name})
    order_form2 = orig_parts.customer_dropbox(order_form2)
    # ページネーション機能
    obj_list = Order.objects.filter(customer_name=customer_name).order_by('-order_datetime')
    page_obj, next, prev = orig_parts.pagenation(request, obj_list)

    params = {
        'order_search_form': order_form2,
        'order_create_form': order_form,
        'order_update_form': OrderUpdateForm(),
        'object_list': page_obj,
        'next_page_href': orig_parts.some_page_href(next, customer_name),
        'prev_page_href': orig_parts.some_page_href(prev, customer_name),
        'customer_name': customer_name
    }

    return render(request, 'sales/order_list.html', params)


#################################
# 受入情報の更新
#################################
def order_update(request, pk):
    if request.method == 'POST':
        customer_name = str(request.POST.get('customer_name'))
        product_name = str(request.POST.get('product_name'))
        volume = Decimal(request.POST.get('volume'))
        total_price = str(request.POST.get('total_price'))
        delivery_date = str(request.POST.get('delivery_date'))
        delivery_status = str(request.POST.get('delivery_status'))
        invoice_status = str(request.POST.get('invoice_status'))
        delivery_number = str(request.POST.get('delivery_number'))
        invoice_number = str(request.POST.get('invoice_number'))
        unit_price = Decimal(request.POST.get('unit_price'))
        unit = str(request.POST.get('unit'))

        # 未納品で請求済に変更できないようにする
        if delivery_status == 'False' and invoice_status == 'True':
            message = "「未納品」の状態で「請求済」に変更することはできません。"
            messages.add_message(request, messages.ERROR, message)
        else:
            # 合計金額の計算([0]:数字、[1]:単位)
            spl = re.match('^(\d{1,10})(.)', unit)
            if spl:
                total_price = volume*(unit_price/Decimal(spl[1]))
            else:
                total_price = volume*unit_price

            # データの更新実行
            if not delivery_date:
                Order.objects.filter(pk=pk).update(unit_price=unit_price, unit=unit, volume=volume, total_price=total_price, delivery_status=delivery_status, delivery_number=delivery_number, invoice_status=invoice_status, invoice_number=invoice_number)
            else:
                Order.objects.filter(pk=pk).update(unit_price=unit_price, unit=unit, volume=volume, total_price=total_price, delivery_date=delivery_date, delivery_status=delivery_status, delivery_number=delivery_number, invoice_status=invoice_status, invoice_number=invoice_number)

            # 更新処理完了後の表示情報のセット
            if not delivery_date:
                delivery_date = '指定なし'
            if delivery_status == 'True':
                delivery_status = '納品済'
            else:
                delivery_status = '未納品'

            if invoice_status == 'True':
                invoice_status = '請求済'
            else:
                invoice_status = '未請求'
            message = "受注情報を更新しました。顧客名：{0}　商品名：{1}　価格：{2}/{3}　数量：{4}　合計：{5}　納品日：{6}, 　状態：{7}/{8},　納品番号：{9},　請求番号：{10}".format(
                customer_name, product_name, unit_price, unit ,volume, total_price, delivery_date, delivery_status, invoice_status, delivery_number, invoice_number
                )
            messages.add_message(request, messages.INFO, message)
    else:
        customer_name = str(request.GET['customer_name'])

    # 商品名のドロップボックスを作成
    order_form = OrderCreateForm()
    order_form = orig_parts.products_dropbox(order_form)
    # 顧客名のドロップボックスを作成
    order_form2 = DeliveryFilterForm({'customer_name': customer_name})
    order_form2 = orig_parts.customer_dropbox(order_form2)
    # ページネーション機能
    obj_list = Order.objects.filter(customer_name=customer_name).order_by('-order_datetime')
    page_obj, next, prev = orig_parts.pagenation(request, obj_list)
    
    params = {
        'order_search_form': order_form2,
        'order_create_form': order_form,
        'order_update_form': OrderUpdateForm(),
        'object_list': page_obj,
        'next_page_href': orig_parts.some_page_href(next, customer_name),
        'prev_page_href': orig_parts.some_page_href(prev, customer_name),
        'customer_name': customer_name
    }

    return render(request, 'sales/order_list.html', params)



#################################
# 受入情報の削除
#################################
def order_delete(request, pk): 
    if request.method == 'POST':
        # 受入情報の削除処理
        object = Order.objects.get(pk=pk)
        customer_name = object.customer_name
        delivery_date = object.delivery_date
        delivery_status = object.delivery_status
        invoice_status = object.invoice_status
        object.delete()

        # 表示用メッセージの成型
        if not delivery_date:
            delivery_date = '指定なし'
        if delivery_status == 'True':
            delivery_status = '納品済'
        else:
            delivery_status = '未納品'

        if invoice_status == 'True':
            invoice_status = '請求済'
        else:
            invoice_status = '未請求'
        
        message = "受注情報を削除しました。顧客名：{0}　商品名：{1}　数量：{2}　合計：{3}　納品日：{4}, 　状態：{5}/{6}".format(
            customer_name, object.product_name, object.volume, object.total_price, delivery_date, delivery_status, invoice_status
            )
        messages.add_message(request, messages.ERROR, message)
    else:
        customer_name = str(request.GET['customer_name'])

    # 商品名のドロップボックスを作成
    order_form = OrderCreateForm()
    order_form = orig_parts.products_dropbox(order_form)
    # 顧客名のドロップボックスを作成
    order_form2 = DeliveryFilterForm({'customer_name': customer_name})
    order_form2 = orig_parts.customer_dropbox(order_form2)
    # ページネーション機能(途中)
    obj_list = Order.objects.filter(customer_name=customer_name).order_by('-order_datetime')
    page_obj, next, prev = orig_parts.pagenation(request, obj_list)

    params = {
        'order_search_form': order_form2,
        'order_create_form': order_form,
        'order_update_form': OrderUpdateForm(),
        'object_list': page_obj,
        'next_page_href': orig_parts.some_page_href(next, customer_name),
        'prev_page_href': orig_parts.some_page_href(prev, customer_name),
        'customer_name': customer_name
    }

    return render(request, 'sales/order_list.html', params)


# 現状なし
# 受入情報検索    
def OrderSearch(request):
    condition_dict = {}
    #print(request.POST)
    # key: パラメータ, value: デフォルト値
    params = {
        'customer_name': '顧客名を選択してください', 
        'product_name': '商品名を選択してください',
        'delivery_date_S': '',
        'delivery_date_E': ''
        }
    # condition_dictへのフィルタ条件の追加
    for key, value in params.items():
        if key in request.POST:
            param = request.POST[key]
            if param != value:
                # 納品日のレンジのための文字列置換
                if key == 'delivery_date_S':
                    condition_dict['delivery_date__gte'] = param
                    continue
                if key == 'delivery_date_E':
                    condition_dict['delivery_date__lte'] = param
                    continue
                condition_dict[key] = param
    
   # condition_dictのフィルタ条件に基づいて検索を実行
    if condition_dict:
        search_list = Order.objects.filter(**condition_dict).order_by('-order_datetime').order_by('-order_datetime')

    else:
        search_list = Order.objects.all().order_by('-order_datetime').order_by('-order_datetime')


    paginator = Paginator(search_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
        
    params = {
        "page_obj": page_obj,
        "order_create_form": OrderCreateForm,
        "order_update_form": OrderUpdateForm,
        "order_search_form": DeliveryFilterForm
    }    

    return render(request, 'sales/order_search.html', params)



#################################
# 納品書作成画面関連
#################################
def delivery_slip(request):
    obj_list = Order.objects.all().order_by('-order_datetime')

    # 商品名のドロップボックスを作成
    order_form = DeliveryFilterForm(request.GET)
    order_form = orig_parts.products_dropbox(order_form)
    # 顧客名のドロップボックスを作成
    order_form = orig_parts.customer_dropbox(order_form)
    # ページネーション機能
    page_obj, next, prev = orig_parts.pagenation(request, obj_list)

    params = {
        'order_search_form': order_form,
        'object_list': page_obj,
        'next_page_href': orig_parts.some_page_href(next, ''),
        'prev_page_href': orig_parts.some_page_href(prev, ''),
        'customer_name': ''
    }

    return render(request, 'sales/delivery_slip.html', params)



#################################
# 納品書発行画面でのフィルタ処理 
#################################
condition_dict = {}
def delivery_search(request):
    if request.method == 'GET':
        customer_name = request.GET.get('customer_name')
        if customer_name == '顧客名を選択してください':
            obj_list = Order.objects.all()

            message = '顧客名を選択してください。'
            messages.add_message(request, messages.ERROR, message)
        else:
            # 顧客名の設定
            condition_dict['customer_name'] = customer_name

            # product_nameが設定されているかの確認
            if request.GET.get('product_name'):
                product_name = request.GET.get('product_name')
                product_name = product_name.split(':')[0]
                condition_dict['product_name'] = product_name
            
            # 納品期間が設定されているかの確認
            if request.GET.get('delivery_date_S'):
                delivery_start = request.GET.get('delivery_date_S')
                condition_dict['delivery_date__gte'] = delivery_start
            if request.GET.get('delivery_date_E'):
                delivery_end = request.GET.get('delivery_date_E')
                condition_dict['delivery_date__lte'] = delivery_end
            
            # 納品状態のフィルタリング
            if request.GET.get('delivery_status'):
                delivery_status = request.GET.get('delivery_status')
                if not delivery_status == '納品状態を選択してください':
                    condition_dict['delivery_status'] = delivery_status

            # 条件リストがあれば、設定された条件でフィルタリングし、なければ当該の顧客名でフィルタリングする
            if condition_dict:
                obj_list = Order.objects.filter(**condition_dict).order_by('-order_datetime')
            else:
                obj_list = Order.objects.filter(customer_name=customer_name).order_by('-order_datetime')

    # 商品名のドロップボックスを作成
    order_form = DeliveryFilterForm(request.GET)
    order_form = orig_parts.products_dropbox(order_form)
    # 顧客名のドロップボックスを作成
    order_form = orig_parts.customer_dropbox(order_form)
    # ページネーション機能
    page_obj, next, prev = orig_parts.pagenation(request, obj_list)
    
    if not request.GET.get('product_name'):
        product_name = ''
    if not request.GET.get('delivery_status'):
        delivery_status = ''
    if not request.GET.get('delivery_date_S'):
        delivery_start = ''
    if not request.GET.get('delivery_date_E'):
        delivery_end = ''
    params = {
        'order_search_form': order_form,
        #'object_list': page_obj,
        'object_list': obj_list,
        #'next_page_href': orig_parts.some_page_href(next, customer_name),
        #'prev_page_href': orig_parts.some_page_href(prev, customer_name),
        'customer_name': customer_name,
        'product_name': product_name,
        'delivery_status': delivery_status,
        'delivery_date_S': delivery_start,
        'delivery_date_E': delivery_end,
    }

    return render(request, 'sales/delivery_slip.html', params)



#################################
# 納品書発行処理
#################################
def create_delivery_slip(request):
    if request.method == 'POST':
        delivery_info = request.POST
        pk_list = list()
        for i in delivery_info:
            result_delivery = re.match('delivery_\d+', i)
            if result_delivery:
                pk = result_delivery.group().split('_')[1]
                pk_list.append(pk)

        if not pk_list:
            customer_name = ''
            message = "納品対象の商品をチェックしてください。"
            messages.add_message(request, messages.ERROR, message)
        else:
            valid = True
            customer_name = Order.objects.get(pk=pk_list[0]).customer_name
            # pk_listで納品済の受注がないかのバリデーション
            for pk in pk_list:
                object = Order.objects.get(pk=pk)
                delivery_status = object.delivery_status
                if delivery_status:
                    message = "納品済の受注商品の納品書発行はできません。(ID={0})".format(pk)
                    messages.add_message(request, messages.ERROR, message)
                    valid = False
                    break
            if valid:              
                # 納品書発行処理
                from . import create_delivery_slip
                pdf_path, tf, message = create_delivery_slip.create_delivery_slip(pk_list, str(delivery_info['delivery_number']))
                if tf:
                    # delivery_statusを更新
                    for pk in pk_list:
                        delivery_date = Order.objects.get(pk=pk).delivery_date
                        if delivery_date:
                            Order.objects.filter(pk=pk).update(delivery_status='True')
                        else:
                            import datetime
                            Order.objects.filter(pk=pk).update(delivery_status='True', delivery_date=datetime.date.today())
                    message = message + '{0}に保存しました。'.format(pdf_path)
                    messages.add_message(request, messages.INFO, message)
                    # PDFファイルのダウンロード
                    response = HttpResponse(open(pdf_path, 'rb').read(), content_type='application/pdf')
                    response['Content-Disposition'] = 'attachment; filename="{0}";'.format(urllib.parse.quote(os.path.basename(pdf_path)))
                    return response
                else:
                    messages.add_message(request, messages.ERROR, message)
    else:
        customer_name = ''

    # 商品名のドロップボックスを作成
    order_form = DeliveryFilterForm()
    order_form = orig_parts.products_dropbox(order_form)
    # 顧客名のドロップボックスを作成
    order_form = orig_parts.customer_dropbox(order_form)
    # ページネーション機能
    obj_list = Order.objects.all().order_by('-order_datetime')
    page_obj, next, prev = orig_parts.pagenation(request, obj_list)

    params = {
        'order_search_form': order_form,
        'object_list': page_obj,
        'next_page_href': orig_parts.some_page_href(next, customer_name),
        'prev_page_href': orig_parts.some_page_href(prev, customer_name),
        'customer_name': customer_name,
    }

    return render(request, 'sales/delivery_slip.html', params)



#################################
# 請求書作成画面関連
#################################
def invoice_slip(request):
    obj_list = Order.objects.all().order_by('-order_datetime')

    # 商品名のドロップボックスを作成
    order_form = DeliveryFilterForm(request.GET)
    order_form = orig_parts.products_dropbox(order_form)
    # 顧客名のドロップボックスを作成
    order_form = orig_parts.customer_dropbox(order_form)
    # ページネーション機能
    page_obj, next, prev = orig_parts.pagenation(request, obj_list)

    params = {
        'order_search_form': order_form,
        'object_list': page_obj,
        'next_page_href': orig_parts.some_page_href(next, ''),
        'prev_page_href': orig_parts.some_page_href(prev, ''),
        'customer_name': ''
    }

    return render(request, 'sales/invoice_slip.html', params)



#################################
# 請求書発行画面でのフィルタ処理 
#################################
condition_dict = {}
def invoice_search(request):
    if request.method == 'GET':
        customer_name = request.GET.get('customer_name')
        if customer_name == '顧客名を選択してください':
            obj_list = Order.objects.all()

            message = '顧客名を選択してください。'
            messages.add_message(request, messages.ERROR, message)
        else:
            # 顧客名の設定
            condition_dict['customer_name'] = customer_name

            # product_nameが設定されているかの確認
            if request.GET.get('product_name'):
                product_name = request.GET.get('product_name')
                product_name = product_name.split(':')[0]
                condition_dict['product_name'] = product_name
            
            # 納品期間が設定されているかの確認
            if request.GET.get('delivery_date_S'):
                delivery_start = request.GET.get('delivery_date_S')
                condition_dict['delivery_date__gte'] = delivery_start
            if request.GET.get('delivery_date_E'):
                delivery_end = request.GET.get('delivery_date_E')
                condition_dict['delivery_date__lte'] = delivery_end
            
            # 納品状態のフィルタリング
            if request.GET.get('delivery_status'):
                delivery_status = request.GET.get('delivery_status')
                if not delivery_status == '納品状態を選択してください':
                    condition_dict['delivery_status'] = delivery_status
            
            # 請求状態のフィルタリング
            if request.GET.get('invoice_status'):
                invoice_status = request.GET.get('invoice_status')
                if not invoice_status == '請求状態を選択してください':
                    condition_dict['invoice_status'] = invoice_status

            # 条件リストがあれば、設定された条件でフィルタリングし、なければ当該の顧客名でフィルタリングする
            if condition_dict:
                obj_list = Order.objects.filter(**condition_dict).order_by('-order_datetime')
            else:
                obj_list = Order.objects.filter(customer_name=customer_name).order_by('-order_datetime')

    # 商品名のドロップボックスを作成
    order_form = DeliveryFilterForm(request.GET)
    order_form = orig_parts.products_dropbox(order_form)
    # 顧客名のドロップボックスを作成
    order_form = orig_parts.customer_dropbox(order_form)
    # ページネーション機能
    page_obj, next, prev = orig_parts.pagenation(request, obj_list)
    
    if not request.GET.get('product_name'):
        product_name = ''
    if not request.GET.get('delivery_status'):
        delivery_status = ''
    if not request.GET.get('delivery_date_S'):
        delivery_start = ''
    if not request.GET.get('delivery_date_E'):
        delivery_end = ''
    params = {
        'order_search_form': order_form,
        #'object_list': page_obj,
        'object_list': obj_list,
        #'next_page_href': orig_parts.some_page_href(next, customer_name),
        #'prev_page_href': orig_parts.some_page_href(prev, customer_name),
        'customer_name': customer_name,
        'product_name': product_name,
        'delivery_status': delivery_status,
        'delivery_date_S': delivery_start,
        'delivery_date_E': delivery_end,
    }

    return render(request, 'sales/invoice_slip.html', params)



#################################
# 請求書発行処理
#################################
def create_invoice_slip(request):
    if request.method == 'POST':
        invoice_info = request.POST
        pk_list = list()
        for i in invoice_info:
            result_invoice = re.match('invoice_\d+', i)
            if result_invoice:
                pk = result_invoice.group().split('_')[1]
                pk_list.append(pk)

        if not pk_list:
            customer_name = ''
            message = "請求対象の商品をチェックしてください。"
            messages.add_message(request, messages.ERROR, message)
        else:
            valid = True
            customer_name = Order.objects.get(pk=pk_list[0]).customer_name
            # pk_listのバリデーション
            for pk in pk_list:
                object = Order.objects.get(pk=pk)
                delivery_status = object.delivery_status
                invoice_status = object.invoice_status
                # pk_listで未納品の受注がないかのバリデーション
                if not delivery_status:
                    message = "未納品の受注商品の請求書発行はできません。(ID={0})".format(pk)
                    messages.add_message(request, messages.ERROR, message)
                    valid = False
                    break
                # pk_listで請求済の受注がないかのバリデーション
                if invoice_status:
                    message = "請求済の受注商品の請求書発行はできません。(ID={0})".format(pk)
                    messages.add_message(request, messages.ERROR, message)
                    valid = False
                    break
            if valid:              
                # 請求書発行処理
                start = invoice_info['invoice_start']
                start = start.replace('-', '/')
                end = invoice_info['invoice_end']
                end = end.replace('-', '/')
                if start == end:
                    duration = start
                elif start == '':
                    duration = ' - ' + end
                elif end == '':
                    duration = start + ' - '
                else:
                    duration = start + ' - ' + end
                
                from . import create_invoice_slip
                pdf_path, tf, message = create_invoice_slip.create_invoice_slip(pk_list, str(invoice_info['invoice_number']), duration)
                if tf:
                    # invoice_statusを更新
                    for pk in pk_list:
                        Order.objects.filter(pk=pk).update(invoice_status='True', invoice_date=datetime.date.today().strftime('%Y-%m-%d'))
                    message = message + '{0}に保存しました。'.format(pdf_path)
                    messages.add_message(request, messages.INFO, message)

                    # PDFファイルのダウンロード
                    response = HttpResponse(open(pdf_path, 'rb').read(), content_type='application/pdf')
                    response['Content-Disposition'] = 'attachment; filename="{0}";'.format(urllib.parse.quote(os.path.basename(pdf_path)))
                    return response
                else:
                    messages.add_message(request, messages.ERROR, message)
    else:
        customer_name = ''

    # 商品名のドロップボックスを作成
    order_form = DeliveryFilterForm()
    order_form = orig_parts.products_dropbox(order_form)
    # 顧客名のドロップボックスを作成
    order_form = orig_parts.customer_dropbox(order_form)
    # ページネーション機能
    #obj_list = Order.objects.filter(customer_name=customer_name)
    obj_list = Order.objects.all().order_by('-order_datetime')
    page_obj, next, prev = orig_parts.pagenation(request, obj_list)

    params = {
        'order_search_form': order_form,
        'object_list': page_obj,
        'next_page_href': orig_parts.some_page_href(next, customer_name),
        'prev_page_href': orig_parts.some_page_href(prev, customer_name),
        'customer_name': customer_name,
        #'response': response
    }

    return render(request, 'sales/invoice_slip.html', params)