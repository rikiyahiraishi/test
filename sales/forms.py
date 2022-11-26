#sales/forms.py
from secrets import choice
from tkinter import Widget
from django import forms
from django.core.validators import validate_integer
from numpy import product
from .models import Order, Products, Customer
import re
#from bootstrap_datepicker_plus import DatePickerInput

# 商品情報管理
class ProductCreateForm(forms.ModelForm):
    class Meta:
        model = Products
        fields = ('name', 'unit_price', 'unit',)
        widgets = {
            'name': forms.TextInput(attrs={'autocomplete': 'off',
                                                  'placeholder': '例：サンプル',
                                                  'class': 'form-control'}),
            'unit_price': forms.TextInput(attrs={'autocomplete': 'off',
                                               'placeholder': '例：1000',
                                               'class': 'form-control'}),
            'unit': forms.TextInput(attrs={'autocomplete': 'off',
                                                 'placeholder': '例：100g',
                                                 'class': 'form-control'}),
        }

    # 単価をバリデーションする
    def clean_unit_price(self):
        form_unit_price = self.cleaned_data['unit_price']
        result_price = re.match(r'^\d+$', form_unit_price)
        
        message = '単価は1円単位の価格（円）（数値のみ）で設定してください。（入力値：{0}）'.format(form_unit_price)
        if not result_price:
            raise forms.ValidationError((message), code='invalid unit proce')

        return form_unit_price
    

    # nameをバリデーションする
    def clean_name(self):
        form_name = self.cleaned_data['name']
        product_tf = Products.objects.filter(name=form_name)

        message = '商品名「{0}」は既に登録されています。'.format(form_name)
        if product_tf:
            raise forms.ValidationError((message), code='invalid name')

        return form_name


class ProductUpdateForm(forms.ModelForm):
    class Meta:
        model = Products
        fields = ('name', 'unit_price', 'unit',)
        widgets = {
            'name': forms.TextInput(attrs={'autocomplete': 'off',
                                                  'placeholder': '例：サンプル',
                                                  'class': 'form-control',
                                                  'id': 'up_name'}),
            'unit_price': forms.TextInput(attrs={'autocomplete': 'off',
                                               'placeholder': '例：1000',
                                               'class': 'form-control',
                                               'id': 'up_unit_price'}),
            'unit': forms.TextInput(attrs={'autocomplete': 'off',
                                                 'placeholder': '例：100g',
                                                 'class': 'form-control',
                                                 'id': 'up_unit'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs['readonly'] = 'readonly'
    
    # 単価をバリデーションする
    def clean_unit_price(self):
        form_unit_price = self.cleaned_data['unit_price']
        result_price = re.match(r'^\d+$', form_unit_price)

        message = '単価は1円単位の価格（円）（数値のみ）で設定してください。（入力値：{0}）'.format(form_unit_price)
        if not result_price:
            raise forms.ValidationError((message), code='invalid unit proce')

        return form_unit_price


class ProductSearchForm(forms.Form):
    freeword = forms.CharField(min_length=1, max_length=30, label='', required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)



# 顧客情報管理
class CustomerCreateForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ('customer_name', 'post_code', 'address', 'phone_number', 'manager',)
        widgets = {
            'customer_name': forms.TextInput(attrs={'autocomplete': 'off',
                                                  'placeholder': '例：〇〇株式会社',
                                                  'class': 'form-control'}),
            'post_code': forms.TextInput(attrs={'autocomplete': 'off',
                                               'placeholder': '例：656-0332',
                                               'class': 'form-control'}),
            'address': forms.TextInput(attrs={'autocomplete': 'off',
                                                 'placeholder': '例：兵庫県南あわじ市湊〇〇-〇',
                                                 'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'autocomplete': 'off',
                                                 'placeholder': '例：0799-36-0000',
                                                 'class': 'form-control'}),
            'manager': forms.TextInput(attrs={'autocomplete': 'off',
                                                 'placeholder': '例：山田　太郎',
                                                 'class': 'form-control'}),
        }

    # customer_nameをバリデーションする
    def clean_customer_name(self):
        form_name = self.cleaned_data['customer_name']
        product_tf = Customer.objects.filter(customer_name=form_name)

        message = '会社名「{0}」は既に登録されています。'.format(form_name)
        if product_tf:
            raise forms.ValidationError((message), code='invalid customer name')

        return form_name
    
    # phone_numberをバリデーションする
    def clean_phone_number(self):
        form_phone_number = self.cleaned_data['phone_number']
        if not form_phone_number:
            form_phone_number = '-'
        
        return form_phone_number
    
    # managerをバリデーションする
    def clean_manager(self):
        form_manager = self.cleaned_data['manager']
        if not form_manager:
            form_manager = '-'
        
        return form_manager


class CustomerUpdateForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ('customer_name', 'post_code', 'address', 'phone_number', 'manager',)
        widgets = {
            'customer_name': forms.TextInput(attrs={'autocomplete': 'off',
                                                  'placeholder': '例：〇〇株式会社',
                                                  'class': 'form-control',
                                                  'id': 'up_customer_name'}),
            'post_code': forms.TextInput(attrs={'autocomplete': 'off',
                                               'placeholder': '例：656-0332',
                                               'class': 'form-control',
                                               'id': 'up_post_code'}),
            'address': forms.TextInput(attrs={'autocomplete': 'off',
                                                 'placeholder': '例：兵庫県南あわじ市湊〇〇-〇',
                                                 'class': 'form-control',
                                                 'id': 'up_address'}),
            'phone_number': forms.TextInput(attrs={'autocomplete': 'off',
                                                 'placeholder': '例：0799-36-0000',
                                                 'class': 'form-control',
                                                 'id': 'up_phone_number'}),
            'manager': forms.TextInput(attrs={'autocomplete': 'off',
                                                 'placeholder': '例：山田　太郎',
                                                 'class': 'form-control',
                                                 'id': 'up_manager'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['customer_name'].widget.attrs['readonly'] = 'readonly'
    
    # phone_numberをバリデーションする
    def clean_phone_number(self):
        form_phone_number = self.cleaned_data['phone_number']
        if not form_phone_number:
            form_phone_number = '-'
        
        return form_phone_number
    
    # managerをバリデーションする
    def clean_manager(self):
        form_manager = self.cleaned_data['manager']
        if not form_manager:
            form_manager = '-'
        
        return form_manager




class CustomerSearchForm(forms.Form):
    freeword = forms.CharField(min_length=1, 
                                max_length=30, label='', required=False, 
                                widget=forms.Select(attrs={'class': 'form-control', 'id': 'customer_search', }),
                    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)



# 受入情報管理
class OrderCreateForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ('customer_name', 'product_name', 'volume', 'delivery_date',)

        widgets = {
            'customer_name': forms.TextInput(attrs={'autocomplete': 'off',
                                               'placeholder': '例：1000',
                                               'class': 'form-control',
                                               'id': 'new_customer_name'}),
            'product_name': forms.Select(attrs={'autocomplete': 'off',
                                               'class': 'form-control',
                                               'id': 'new_product_name'}),
            'volume': forms.TextInput(attrs={'autocomplete': 'off',
                                               'placeholder': '例：1000',
                                               'class': 'form-control'}),
            'delivery_date': forms.NumberInput(attrs={'autocomplete': 'off',
                                                 'placeholder': '例：2022-12-31',
                                                 'class': 'form-control',
                                                 'type':'date'}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['customer_name'].widget.attrs['readonly'] = 'readonly'
        #self.fields['product_name'].initial = 'aa'

    # 顧客名をバリデーションする
    def clean_customer_name(self):
        form_customer_name = self.cleaned_data['customer_name']
        message = '顧客名が選択されていません。'
        if form_customer_name == '顧客名を選択してください':
            raise forms.ValidationError((message), code='invalid customer name')
        
        return form_customer_name
    
    # 商品名をバリデーションする
    def clean_product_name(self):
        form_product_name = self.cleaned_data['product_name']
        message = '商品名が選択されていません。'
        if form_product_name == '商品名を選択してください':
            raise forms.ValidationError((message), code='invalid product name')
        
        return form_product_name


class OrderUpdateForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ('customer_name', 'product_name', 'volume', 'total_price', 'delivery_date', 'delivery_status', 'invoice_status', 'delivery_number', 'invoice_number', 'unit_price', 'unit', )
        widgets = {
            
            'customer_name': forms.TextInput(attrs={'autocomplete': 'off',
                                               'placeholder': '例：〇〇株式会社',
                                               'class': 'form-control',
                                               'id': 'up_customer_name'}),
            'product_name': forms.TextInput(attrs={'autocomplete': 'off',
                                                 'placeholder': '例：商品名',
                                                 'class': 'form-control',
                                                 'id': 'up_product_name'}),
            'volume': forms.TextInput(attrs={'autocomplete': 'off',
                                                  'placeholder': '例：100',
                                                  'class': 'form-control',
                                                  'id': 'up_volume'}),
            'total_price': forms.TextInput(attrs={'autocomplete': 'off',
                                               'placeholder': '例：1000',
                                               'class': 'form-control',
                                               'id': 'up_total_price'}),
            'delivery_date': forms.NumberInput(attrs={'autocomplete': 'off',
                                                 'placeholder': '例：2022/12/31',
                                                 'class': 'form-control',
                                                 'type':'date',
                                                 'id': 'up_delivery_date'}),
            'delivery_status': forms.Select(choices = (('False', '未納品'), ('True', '納品済'),),
                                            attrs={'class': 'form-control', 
                                            'id': 'up_delivery_status'}),
            'invoice_status': forms.Select(choices = (('False', '未請求'), ('True', '請求済'),),
                                            attrs={'class': 'form-control', 
                                            'id': 'up_invoice_status'}),
            'delivery_number': forms.TextInput(attrs={'autocomplete': 'off',
                                               'placeholder': '',
                                               'class': 'form-control',
                                               'id': 'up_delivery_number'}),
            'invoice_number': forms.TextInput(attrs={'autocomplete': 'off',
                                               'placeholder': '',
                                               'class': 'form-control',
                                               'id': 'up_invoice_number'}),
            'unit_price': forms.TextInput(attrs={'autocomplete': 'off',
                                                 'placeholder': '例：1000',
                                                 'class': 'form-control',
                                                 'id': 'up_unit_price'}),
            'unit': forms.TextInput(attrs={'autocomplete': 'off',
                                                 'placeholder': '例：100g',
                                                 'class': 'form-control',
                                                 'id': 'up_unit'}),
            
        } 
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['customer_name'].widget.attrs['readonly'] = 'readonly'
        self.fields['product_name'].widget.attrs['readonly'] = 'readonly'
        self.fields['total_price'].widget.attrs['readonly'] = 'readonly'
    
    # 請求状態をバリデーションする（未納品の場合、請求済に変更できないようする）
    def clean_invoice_status(self):
        form_invoice_status = self.cleaned_data['invoice_status']
        form_delivery_status = self.cleaned_data['delivery_status']
        if form_invoice_status == True:
            if form_delivery_status == False:
                message = '納品状態が「未納品」では、請求状態を「請求済」に変更できません。'
                raise forms.ValidationError((message), code='invalid invoice status')
        
        return form_invoice_status
    
    # 単価をバリデーションする
    def clean_unit_price(self):
        form_unit_price = self.cleaned_data['unit_price']
        result_price = re.match(r'^\d+$', form_unit_price)

        message = '単価は1円単位の価格（円）（数値のみ）で設定してください。（入力値：{0}）'.format(form_unit_price)
        if not result_price:
            raise forms.ValidationError((message), code='invalid unit proce')

        return form_unit_price




class DeliveryFilterForm(forms.Form):
    product_name = forms.ChoiceField(
                    required = False,
                    label='商品名',
                    widget=forms.Select(attrs={'class': 'form-control', 'id': 'product_name', 'disabled': 'disabled'}),
                    )
    customer_name = forms.ChoiceField(
                    required = False,
                    label='顧客名',
                    widget=forms.Select(attrs={'class': 'form-control', 'id': 'customer_name', 'name': 'customer_name'}),
                    )
    delivery_date_S = forms.DateField(
                                required = False,
                                widget=forms.NumberInput(attrs={'class': 'form-control', 'type':'date', 'id': 'delivery_date_S', 'disabled': 'disabled'})
                                )
    delivery_date_E = forms.DateField(
                                required = False,
                                widget=forms.NumberInput(attrs={'class': 'form-control', 'type':'date', 'id': 'delivery_date_E', 'disabled': 'disabled'})
                                )
    delivery_status = forms.ChoiceField(
                    choices = (('納品状態を選択してください', '納品状態を選択してください ▼'), (False, '未納品'), (True, '納品済')),
                    required = False,
                    label='納品状態',
                    widget=forms.Select(attrs={'class': 'form-control', 'id': 'delivery_status', 'name': 'delivery_status', 'disabled': 'disabled'}),
                    )
    invoice_status = forms.ChoiceField(
                    choices = (('請求状態を選択してください', '請求状態を選択してください ▼'), (False, '未請求'), (True, '請求済')),
                    required = False,
                    label='請求状態',
                    widget=forms.Select(attrs={'class': 'form-control', 'id': 'invoice_status', 'name': 'invoice_status', 'disabled': 'disabled'}),
                    )
    delivery_number = forms.DateField(
                    widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '納品番号を入力', 'id': 'delivery_number', 'name': 'delivery_number'})
                    )
    invoice_number = forms.DateField(
                    widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '請求番号を入力', 'id': 'invoice_number', 'invoice': 'delivery_number'})
                    )