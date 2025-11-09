from flask import Blueprint, render_template, request, url_for, redirect, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from link import *
from api.sql import *
import imp, random, os, string
from werkzeug.utils import secure_filename
from flask import current_app

UPLOAD_FOLDER = 'static/product'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

manager = Blueprint('manager', __name__, template_folder='../templates')

def config():
    current_app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    config = current_app.config['UPLOAD_FOLDER'] 
    return config

@manager.route('/', methods=['GET', 'POST'])
@login_required
def home():
    return redirect(url_for('manager.productManager'))

@manager.route('/productManager', methods=['GET', 'POST'])
@login_required
def productManager():
    if request.method == 'GET':
        if(current_user.role == 'user'):
            flash('No permission')
            return redirect(url_for('index'))
        
    if 'delete' in request.values:
        pid = request.values.get('delete')
        data = Record.delete_check(pid)
        
        if(data != None):
            flash('failed')
        else:
            data = Product.get_product(pid)
            Product.delete_product(pid)
    
    elif 'edit' in request.values:
        pid = request.values.get('edit')
        return redirect(url_for('manager.edit', pid=pid))
    
    book_data = book()
    return render_template('productManager.html', book_data = book_data, user=current_user.name)

def book():
    book_row = Product.get_all_product()
    book_data = []
    for i in book_row:
        book = {
            '商品編號': i[0],
            '商品名稱': i[1],
            '商品售價': i[2],
            '商品類別': i[7]
        }
        book_data.append(book)
    return book_data

@manager.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':

        # 產生唯一 pid
        data = ""
        while data is not None:
            number = str(random.randrange(10000, 99999))
            #en = random.choice(string.ascii_letters)
            #movie_id = en + number
            movie_id = number
            data = Product.get_product(movie_id)

        # 取得前端表單資料
        movie_name = request.values.get('m_name')
        rating = request.values.get('rating')
        actor = request.values.get('a_name')
        length = request.values.get('m_length')
        start_date = request.values.get('S_date')
        end_date = request.values.get('E_date')
        price = request.values.get('m_price')
        intro = request.values.get('m_intro')

        # 必填欄位檢查
        if not all([movie_name, rating, actor, length, start_date, end_date, price, intro]):
            flash('所有欄位都是必填的，請確認輸入內容。')
            return redirect(url_for('manager.productManager'))

        # 送進資料庫
        Product.add_product({
            'movie_id': movie_id,
            'movie_name': movie_name,
            'level': rating,
            'actor': actor,
            'length': length,
            'start_time': start_date,
            'end_time': end_date,
            'movie_price': price,
            'introduction': intro
        })

        return redirect(url_for('manager.productManager'))

    return render_template('productManager.html')

@manager.route('/edit', methods=['GET', 'POST'])
@login_required
def edit():
    if request.method == 'GET':
        if(current_user.role == 'user'):
            flash('No permission')
            return redirect(url_for('bookstore'))

    if request.method == 'POST':
        Product.update_product(
            {
            'movie_name' : request.values.get('movie_name'),
            'price' : request.values.get('price'),
            'category' : request.values.get('category'), 
            'pdesc' : request.values.get('description'),
            'pid' : request.values.get('pid')
            }
        )
        
        return redirect(url_for('manager.productManager'))

    else:
        product = show_info()
        return render_template('edit.html', data=product)


def show_info():
    pid = request.args['pid']
    data = Product.get_product(pid)
    pname = data[1]
    price = data[2]
    category = data[3]
    description = data[4]

    product = {
        '商品編號': pid,
        '商品名稱': pname,
        '單價': price,
        '類別': category,
        '商品敘述': description
    }
    return product


@manager.route('/orderManager', methods=['GET', 'POST'])
@login_required
def orderManager():
    if request.method == 'POST':
        pass
    else:
        order_row = Order_List.get_order()
        order_data = []
        for i in order_row:
            full_name = ""
            if not i[1]: 
                full_name = i[2]  # 如果姓是空的，直接使用名字(這時是全名)
            else:
                full_name = f"{i[1]}{i[2]}" # 否則，正常組合
            order = {
                '訂單編號': i[0],
                '訂購人': full_name,
                '訂單總價': i[3],
                '訂單時間': i[4]
            }
            order_data.append(order)
            
        orderdetail_row = Order_List.get_orderdetail()
        order_detail = []

        for j in orderdetail_row:
            orderdetail = {
                '訂單編號': j[0],
                '商品名稱': j[1],
                '商品單價': j[2],
                '訂購數量': j[3]
            }
            order_detail.append(orderdetail)

    return render_template('orderManager.html', orderData = order_data, orderDetail = order_detail, user=current_user.name)