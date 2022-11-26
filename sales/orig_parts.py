from .models import Products, Customer
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


# 商品名のドロップボックスを作成
def products_dropbox(form):
    choice_list = list()
    choice_list.append(('商品名を選択してください', '商品名を選択してください ▼')) 
    object_list = Products.objects.all().values()
    for i in range(len(object_list)):
        choice_list.append((object_list[i]['name']+':'+object_list[i]['unit_price']+'円 / '+object_list[i]['unit'], object_list[i]['name']))    
    form.fields['product_name'].widget.choices = choice_list

    return form



# 顧客名のドロップボックスを作成
def customer_dropbox(form):
    choice_list2 = list()
    choice_list2.append(('顧客名を選択してください', '顧客名を選択してください ▼')) 
    object_list2 = Customer.objects.all().values()
    for i in range(len(object_list2)):
        choice_list2.append((object_list2[i]['customer_name'], object_list2[i]['customer_name']))   
    form.fields['customer_name'].widget.choices = choice_list2

    return form



# ページネーション機能
def pagenation(request, obj_list, item_number=10):
    paginator = Paginator(obj_list, item_number)
    page = request.GET.get('page')
    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    
    if page:
        next_page = int(page)+1
        prev_page = int(page)-1
    else:
        next_page = 2
        prev_page = 1

    return page_obj, next_page, prev_page



# URLの結合処理
def some_page_href(current_page, customer_name, freeword=''):
    params = []
    if current_page:
        params.append('page=%s' % str(current_page))
    if customer_name:
        params.append('customer_name=%s' % str(customer_name))
    if freeword:
        params.append('freeword=%s' % str(freeword))

    return '?' + '&'.join(params)