import re
from typing_extensions import Self
from flask import Flask, request, template_rendered, Blueprint
from flask import url_for, redirect, flash
from flask import render_template
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from datetime import datetime
from numpy import identity, product
import random, string
from sqlalchemy import null
from link import *
import math
from base64 import b64encode
from api.sql import Member, Order_List, Product, Record, Cart,DB,Showtime,Booking
from flask import render_template, request, url_for, redirect
from flask_login import login_required, current_user


store = Blueprint('bookstore', __name__, template_folder='../templates')

@store.route('/', methods=['GET', 'POST'])
@login_required
def bookstore():
    result = Product.count()
    count = math.ceil(result[0]/9)
    flag = 0
    
    if request.method == 'GET':
        if(current_user.role == 'manager'):
            flash('No permission')
            return redirect(url_for('manager.home'))

    if 'keyword' in request.args and 'page' in request.args:
        total = 0
        single = 1
        page = int(request.args['page'])
        start = (page - 1) * 9
        end = page * 9
        search = request.values.get('keyword')
        keyword = search
        
        cursor.execute('SELECT * FROM movie WHERE movie_name LIKE %s', ('%' + search + '%',))
        movie_row = cursor.fetchall()
        movie_data = []
        final_data = []
        
        for i in movie_row:
            movie = {
                '電影編號': i[0],
                '電影名稱': i[1],
                '電影價格': i[7]
            }
            movie_data.append(movie)
            total = total + 1
        
        if(len(movie_data) < end):
            end = len(movie_data)
            flag = 1
            
        for j in range(start, end):
            final_data.append(movie_data[j])
            
        count = math.ceil(total/9)

        return render_template('bookstore.html', single=single, keyword=search, movie_data=movie_data, user=current_user.name, page=1, flag=flag, count=count)

    
    elif 'movie_id' in request.args:
        movie_id = request.args['movie_id']
        data = Product.get_movie(movie_id)
        session_data = Showtime.get_movie_session(movie_id)
        movie_name = data[1]
        level = data[2]
        actor = data[3]
        length = data[4]
        start_time = data[5]
        end_time = data[6]
        movie_price = data[7]
        introduction = data[8]
        
        
        image = '電影名稱'
        
        movie = {
            '電影編號': movie_id,
            '電影名稱': movie_name,
            '分級': level,
            '單價': movie_price,
            '演員': actor,
            '片長': length,
            '開始時間': start_time,
            '結束時間': end_time,
            '商品圖片': image,
            '電影介紹': introduction
        }
        
        
        return render_template('product.html', data = movie, session_data = session_data, user=current_user.name)
    
    elif 'page' in request.args:
        page = int(request.args['page'])
        start = (page - 1) * 9
        end = page * 9
        
        movie_row = Product.get_all_product()
        movie_data = []
        final_data = []
        
        for i in movie_row:
            movie = {
                '電影編號': i[0],
                '電影名稱': i[1],
                '電影價格': i[7]
            }
            movie_data.append(movie)
            
        if(len(movie_data) < end):
            end = len(movie_data)
            flag = 1
            
        for j in range(start, end):
            final_data.append(movie_data[j])

        return render_template('bookstore.html', movie_data=final_data, user=current_user.name, page=page, flag=flag, count=count)

    elif 'keyword' in request.args:
        single = 1
        search = request.values.get('keyword')
        keyword = search
        cursor.execute('SELECT * FROM movie WHERE movie_name LIKE %s', ('%' + search + '%',))
        movie_row = cursor.fetchall()
        movie_data = []
        total = 0
        
        for i in movie_row:
            movie = {
                '電影編號': i[0],
                '電影名稱': i[1],
                '電影價格': i[7]
            }
            movie_data.append(movie)
            total = total + 1
            
        if(len(movie_data) < 9):
            flag = 1

        count = math.ceil(total/9)

        return render_template('bookstore.html', keyword=search, single=single, movie_data=movie_data, user=current_user.name, page=1, flag=flag, count=count)
    
    else:
        movie_row = Product.get_all_product()
        movie_data = []
        temp = 0
        for i in movie_row:
            movie = {
                '電影編號': i[0],
                '電影名稱': i[1],
                '電影價格': i[7]
            }
            if len(movie_data) < 9:
                movie_data.append(movie)

        return render_template('bookstore.html', movie_data=movie_data, user=current_user.name, page=1, flag=flag, count=count)

# 會員購物車
@store.route('/cart')
@login_required
def cart():
    session_id = request.args.get('session_id') 

    if not session_id:
        return redirect(url_for('bookstore.bookstore'))

    showtime_details = Showtime.get_details_for_checkout(session_id)
    
    if not showtime_details:
        return redirect(url_for('bookstore.bookstore'))

    return render_template(
        'checkout.html',
        showtime=showtime_details
    )


@store.route('/order')
def order():
    data = Cart.get_cart(current_user.id)
    tno = data[2]

    product_row = Record.get_record(tno)
    product_data = []

    for i in product_row:
        pname = Product.get_name(i[1])
        product = {
            '商品編號': i[1],
            '商品名稱': pname,
            '商品價格': i[3],
            '數量': i[2]
        }
        product_data.append(product)
    
    total = float(Record.get_total(tno))  # 將 Decimal 轉換為 float


    return render_template('order.html', data=product_data, total=total, user=current_user.name)

@store.route('/orderlist')
def orderlist():
    if "oid" in request.args :
        pass
    
    user_id = current_user.id

    data = Member.get_order(user_id)
    orderlist = []

    for i in data:
        temp = {
            '訂單編號': i[0],
            '訂單總價': i[3],
            '訂單時間': i[2]
        }
        orderlist.append(temp)
    
    orderdetail_row = Order_List.get_orderdetail()
    orderdetail = []

    for j in orderdetail_row:
        temp = {
            '訂單編號': j[0],
            '商品名稱': j[1],
            '商品單價': j[2],
            '訂購數量': j[3]
        }
        orderdetail.append(temp)


    return render_template('orderlist.html', data=orderlist, detail=orderdetail, user=current_user.name)

def change_order():
    data = Cart.get_cart(current_user.id)
    tno = data[2] # 使用者有購物車了，購物車的交易編號是什麼
    product_row = Record.get_record(data[2])

    for i in product_row:
        
        # i[0]：交易編號 / i[1]：商品編號 / i[2]：數量 / i[3]：價格
        if int(request.form[i[1]]) != i[2]:
            Record.update_product({
                'amount':request.form[i[1]],
                'pid':i[1],
                'tno':tno,
                'total':int(request.form[i[1]])*int(i[3])
            })
            print('change')

    return 0


def only_cart():
    count = Cart.check(current_user.id)

    if count is None:
        return 0

    data = Cart.get_cart(current_user.id)
    tno = data[2]
    product_row = Record.get_record(tno)
    product_data = []

    for i in product_row:
        pid = i[1]
        pname = Product.get_name(i[1])
        price = i[3]
        amount = i[2]

        product = {
            '商品編號': pid,
            '商品名稱': pname,
            '商品價格': price,
            '數量': amount
        }
        product_data.append(product)

    return product_data


@store.route('/process_payment_no_seat', methods=['POST'])
@login_required
def process_payment_no_seat():
    # 1. 從 "結帳頁" 的表單接收所有資料
    session_id = request.form.get('session_id')
    theater_id = request.form.get('theater_id')
    quantity_str = request.form.get('quantity')
    pay_total_str = request.form.get('pay') # 這是總金額 (字串)
    card_num = request.form.get('card_num')
    bank_num_str = request.form.get('bank_num')

    # 2. 獲取登入者 ID
    member_id = current_user.id 

    try:
        # 3. 呼叫 SQL 函式 (步驟一)，將「一筆」交易寫入資料庫
        Booking.create_ticket(
            member_id=member_id,
            theater_id=int(theater_id),
            session_id=int(session_id),
            quantity=int(quantity_str),       # [修正] 欄位為 bigint
            pay=int(float(pay_total_str)),    # [修正] 欄位為 bigint
            card_num=card_num,
            bank_num=int(bank_num_str)        # 欄位為 bigint
        )
        
        # 4. 成功：導入回主頁 (電影列表)
        return redirect(url_for('bookstore.bookstore'))

    except Exception as e:
        # 5. 失敗：在伺服器後台印出錯誤
        print(f"訂票失敗，錯誤: {e}") 
        
        # 導回結帳頁
        return redirect(url_for('bookstore.cart', session_id=session_id))