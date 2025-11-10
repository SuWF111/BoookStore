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

    if 'detail' in request.form:
        pid = request.values.get('detail')
        return redirect(url_for('manager.detailPage', pid=pid))


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
            'pid' : request.values.get('pid'),
            'movie_name' : request.values.get('movie_name'),
            'level' : request.values.get('level'),
            'actor' : request.values.get('actor'), 
            'length' : request.values.get('length'),
            'start_time' : request.values.get('start_time'),
            'end_time' : request.values.get('end_time'), 
            'movie_price' : request.values.get('movie_price'),
            'introduction' : request.values.get('introduction')
            }
        )
        
        return redirect(url_for('manager.productManager'))

    else:
        movie = show_info()
        return render_template('edit.html', data=movie)

@manager.route('/detail/<pid>')
def detailPage(pid):
        data = Product.get_movie(pid)
        # count = Ticket.count_ticket(pid)
        # session_data = Session.get_movie_session(pid)
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
            '電影編號': pid,
            '電影名稱': movie_name,
            '分級': level,
            '單價': movie_price,
            '演員': actor,
            '片長': length,
            '開始時間': start_time,
            '結束時間': end_time,
            '商品圖片': image,
            '電影介紹': introduction,
            # '售出票數': count
        }
        return render_template('detail.html', data = movie, user=current_user.name)
    # data = Product.get_movie( pid)
    # return render_template('detail.html', data=data)

@manager.route('/check_tickets', methods=['POST'])
def check_tickets():
    # 從表單接收資料
    movie_id = request.form.get('movie_id')
    theater_id = request.form.get('theater_id')
    session_id = request.form.get('session_id')
    
    # 呼叫已修正的函式
    ticket_data = Ticket.count_ticket(movie_id, theater_id, session_id)

    # 處理查詢結果 (fetchone 會回傳一個元組, 像 (25,) 或 (None,))
    sold_count = 0
    if ticket_data and ticket_data[0] is not None:
        sold_count = ticket_data[0]

    # 建立一個快閃訊息來顯示結果
    # (您可能需要一個函式來把 theater_id 換成中文名稱，但我們先用 ID)
    flash(f"查詢結果：影城 {theater_id}、場次 {session_id}，目前已售出 {sold_count} 張票。", "info") # "info" 是一個類別，用於 Bootstrap 樣式

    # 【完成 return】
    # 將使用者重新導向回他們剛剛所在的電影詳細頁面
    return redirect(url_for('manager.detailPage', pid=movie_id))

def show_info():
    movie_id = request.args['pid']
    data = Product.get_movie(movie_id)
    movie_name = data[1]
    level = data[2]
    actor = data[3]
    length = data[4]
    start_time = data[5]
    end_time = data[6]
    movie_price = data[7]
    introduction = data[8]

    movie = {
        '電影編號': movie_id,
        '電影名稱': movie_name,
        '分級': level,
        '單價': movie_price,
        '演員': actor,
        '片長': length,
        '開始時間': start_time,
        '結束時間': end_time,
        # '商品圖片': image,
        '電影介紹': introduction,
        # '售出票數': count
    }
    return movie


@manager.route('/orderManager', methods=['GET', 'POST'])
@login_required
def orderManager():
    if request.method == 'POST':
        pass
    else:
        order_row = Order_List.get_ticket()
        order_data = []
        for i in order_row:
            order = {
                '訂單編號': i[0],
                '訂購人': i[1],
                '訂單總價': i[2],
                '訂單時間': i[3]
            }
            order_data.append(order)
        # print(order)
   
        orderdetail_row = Order_List.get_ticketdetail()
        
        order_detail = []

        for j in orderdetail_row:
            orderdetail = {
                '訂單編號': j[0],
                '商品名稱': j[1],
                '商品單價': j[2],
                '訂購數量': j[3]
            }
            order_detail.append(orderdetail)
            
        # print(order_detail)

    return render_template('orderManager.html', orderData = order_data, orderDetail = order_detail, user=current_user.name)