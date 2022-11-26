from lib2to3.pgen2.pgen import DFAState
from .models import Products, Customer, Order

import pandas as pd
import openpyxl
import sys
import argparse
import os
import re
import datetime

import xlwings as xw
from . import log_out

##########################################################################
file_path = "C:/Users/rikiya/Desktop/web_app/config/_format/請求書作成.xlsx"
log_dir = "C:/Users/rikiya/Desktop/web_app/config/_log"
# 請求書シートのPDF出力
invoice_pdf_dir = "C:/Users/rikiya/Desktop/"
##########################################################################

def invoice_write(df, invoice_date, invoice_number, invoice_period, post_code, address, company_name, logging):
    try:
        status = True
        # 請求書シートをアクティブシートに設定
        active_sht = xw.sheets["請求書"]
        active_sht.activate()

        # 宛先会社情報の入力
        xw.Range("A5").value = "〒 " + post_code
        xw.Range("A6").value = "    " + address
        xw.Range("A7").value = company_name

        # 請求番号、請求日の書き込み
        xw.Range("I5").value = invoice_number
        xw.Range("I6").value = invoice_date

        # 請求期間の書き込み
        xw.Range("B10").value = invoice_period

        # 前回のデータ削除
        tf = del_past_data(active_sht, logging)
        if not tf:
            # エラーを出力する
            logging.error("前回データを削除できなったので、終了します。")
            logging.info("Process End ---make_invoice---")
            sys.exit()

        # データの成型
        row_list = []
        # [0]:受注日時、[1]:受注番号、[2]:納品日、[3]:商品名、[4]:数量、[5]:単位、[6]:単価、[7]:金額
        for index, row in df.iterrows():
            new_row = [row[0], row[1],  "",  "",  "", row[2], row[3], row[4], row[5], row[6]]
            row_list.append(new_row)
        # 「以下余白」の追加
        row_list.append(["以下余白", "" , "" , "" , "", "", "", "", "", ""])

        # row_listの行数をカウントし、データ数が25件より多い場合は、その分だけ行を追加する
        if len(row_list) > 25:
            for i in range(len(row_list)-25):
                active_sht.range('18:18').insert(shift='down')
                active_sht.range('B18:E18').merge()

        # 納品商品データの書き込み
        xw.Range("A17").value = row_list

    except Exception as err:
        logging.exception(err)

        # Excelファイルの終了
        app = xw.apps.active
        app.quit()

        logging.info("Process Failed ---make_invoiceslip---")
        status = False

    return active_sht, status



def del_past_data(active_sht, logging):
    target_col = "A"
    status = True
    try:
        # A列の最終行を取得
        lwr_r_cell = active_sht.cells.last_cell
        lwr_row = lwr_r_cell.row
        lwr_cell = active_sht.range((lwr_row, target_col))

        if lwr_cell.value is None:
           lwr_cell = lwr_cell.end('up')
        # 最終行
        last_row = lwr_cell.row

        # 最終行が15以下ならデータが存在しないので、14に設定
        if last_row <= 17:
            last_row = 17

        data_range = "A17:J{0}".format(last_row)
        # 前回のデータ削除
        xw.Range(data_range).clear_contents()

        # 複数ぺージになっていた場合に、単一ページに戻す（削除）
        if last_row > 41:
            for i in range(last_row - 41):
                active_sht.range("18:18").delete()

    except Exception as err:
        logging.exception(err)

        # Excelファイルの終了
        app = xw.apps.active
        app.quit()

        # 正常に終了しなかったことを表示
        status = False

        logging.info("Process End ---make_invoice---")
        sys.exit()


    return status



def list_to_df(pk_list):
    df_list = list()
    a = pk_list
    for pk in pk_list:
        object = Order.objects.get(pk=pk)
        order_datetime = object.order_datetime
        order_date = order_datetime.date()
        delivery_date = object.delivery_date
        product_name = object.product_name
        volume = object.volume
        unit_price = object.unit_price
        unit = object.unit
        total_price = object.total_price

        df_list.append([order_date, product_name, volume, unit_price, unit, delivery_date, total_price])

    df = pd.DataFrame(df_list)

    return df



def create_invoice_slip(pk_list, invoice_number, invoice_period):
    try:
        # ログモジュールの初期化
        logging = log_out.setup_logging(log_dir)
        logging.info("Process Start ---make_invoiceslip---")

        # xlwingsでのエクセルファイルの読み込み
        input_book = xw.Book(file_path)

        # シートの読み込み
        sheet_obj = xw.sheets
        # シート名のリスト化
        sheet_list = []
        for i in range(len(sheet_obj)):
            sheet_list.append(xw.sheets[i].name)

        # 納品書シートの存在確認
        if not "請求書" in sheet_list:
            logging.error("「請求書」シートが存在しません。")
            logging.info("Process End ---make_invoiceslip---")
            return '', False
        
        # pk_listのdf化
        df = list_to_df(pk_list)

        # pk_listから顧客情報を取得
        customer_name = Order.objects.get(pk=pk_list[0]).customer_name
        customer_info = Customer.objects.get(customer_name=customer_name)
        address = customer_info.address
        post_code = customer_info.post_code

        # 納品書シートデータの書き込み
        if not invoice_number:
            invoice_number = "-"
        today = datetime.date.today()
        active_sht, status = invoice_write(df, today, invoice_number, invoice_period, post_code, address, customer_name, logging)

        # 書き込みに失敗したら処理を終了する
        if not status:
            message = '請求書の書き込み処理に失敗しました。ログ内容を管理者に連絡してください。'
            return '', False, message

        # PDFファイルパスの生成
        # ディレクトリが存在しない場合は、ディレクトリを作成
        invoice_dir = "{0}/{1}/{2}/{3}/{4}/".format(invoice_pdf_dir, "web_app", customer_name, "請求書", today.year)
        if not os.path.exists(invoice_dir):
            os.makedirs(invoice_dir, exist_ok=False)

        # ファイル一覧を取得
        files_list = os.listdir(invoice_dir)
        # ディレクトリを除き、ファイルのみを一覧に編集
        files_list = [s for s in files_list if re.match('\d{8}_請求書_.+_\d+\.pdf', s)] 

        # ファイルが存在しない場合の処理
        date = today.strftime('%Y%m%d')
        if not files_list:
            new_file_name = "{0}_請求書_{1}_0001.pdf".format("".join(date), customer_name)
        else:
            # 連番の中で最新の番号を取得し、次の番号を設定する
            files_list.sort()
            last_file = files_list[-1]
            file_num = last_file.split("_")[-1]
            file_num = file_num.split(".")[-2]
            next_num = int(file_num) + 1

            diff = len(file_num) - len(str(next_num))

            zero_num = ""
            for i in range(diff):
                zero_num = zero_num + "0"

            new_num = zero_num + str(next_num)
            pre_file = "{0}_請求書_{1}".format("".join(date), customer_name)
            new_file_name = "{0}_{1}.pdf".format(pre_file, new_num)

        #ファイル名の生成
        new_file_path = os.path.join(invoice_dir, new_file_name)
        # PDFファイルの出力
        active_sht.to_pdf(path=new_file_path, show=False)

        # bookの保存
        input_book.save()
        app = xw.apps.active
        app.quit()
    
    except Exception as err:
        logging.exception(err)
        logging.info("Process End ---make_invoiceslip---")

        # Excelファイルの終了
        app = xw.apps.active
        app.quit()

        # 正常に終了しなかったことを通知
        message = '請求書の作成処理に失敗しました。ログ内容を管理者に連絡してください。'
        return '', False, message

    return new_file_path, True, '請求書作成処理が正常に完了しました。'