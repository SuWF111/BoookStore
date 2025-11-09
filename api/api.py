import imp
from flask import render_template, Blueprint, redirect, request, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from link import *
from api.sql import *
from datetime import datetime

api = Blueprint('api', __name__, template_folder='./templates')

login_manager = LoginManager(api)
login_manager.login_view = 'api.login'
login_manager.login_message = "請先登入"

class User(UserMixin):
    pass

@login_manager.user_loader
def user_loader(userid):  
    user = User()
    user.id = userid
    data = Member.get_role(userid)
    try:
        user.role = data[0]
        if not data[1]:
            user.name = data[2]
        else:
            user.name = data[1]+data[2]
    except:
        pass
    return user

@api.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':

        account = request.form['account']
        password = request.form['password']
        data = Member.get_member(account) 

        try:
            DB_password = data[0][1]
            user_id = data[0][2]
            identity = data[0][3]

        except:
            flash('*沒有此帳號')
            return redirect(url_for('api.login'))

        if(DB_password == password ):
            user = User()
            user.id = user_id
            login_user(user)

            if( identity == 'user'):
                return redirect(url_for('bookstore.bookstore'))
            else:
                return redirect(url_for('manager.productManager'))
        
        else:
            flash('*密碼錯誤，請再試一次')
            return redirect(url_for('api.login'))

    
    return render_template('login.html')

@api.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        user_account = request.form['account']
        exist_account = Member.get_all_account()
        account_list = []
        for i in exist_account:
            account_list.append(i[0])

        if(user_account in account_list):
            flash('Falied!')
            return redirect(url_for('api.register'))
        else:
            input = { 
                'lname': request.form['userlname'], 
                'fname': request.form['userfname'], 
                'account':user_account, 
                'password':request.form['password'], 
                'identity':request.form['identity'] 
            }
            Member.create_member(input)
            return redirect(url_for('api.login'))

    return render_template('register.html')

@api.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))
#京緯新增
class Showtime:
    @staticmethod
    def get_details_for_checkout(session_id):
        """
        [已更新] 使用 session_id 查詢結帳所需的資訊。
        """
        sql = """
            SELECT 
                ms.session_id, 
                ms.theater_id,
                ms.session_time,
                m.movie_name,
                m.price
            FROM 
                movie_session ms
            JOIN 
                movie m ON ms.movie_id = m.movie_id
            WHERE 
                ms.session_id = %s;
        """
        return DB.fetchone(sql, (session_id,))


class Booking:
    @staticmethod
    def create_ticket(member_id, theater_id, session_id, quantity, pay, card_num, bank_num):
        """
        [已更新] 根據 'ticket' 表的欄位順序 寫入訂票紀錄。
        """
        # SQL 欄位順序完全匹配您的 'ticket' 表截圖
        sql = """
            INSERT INTO ticket 
            (ticket_id, member_id, theater_id, session_id, trade_time, pay, card_num, bank_num, quantity)
            VALUES (DEFAULT, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        trade_time = datetime.now() 
        
        # 準備要插入的資料 (順序必須對應 SQL 中的 %s)
        input_data = (
            member_id,    # %s 1
            theater_id,   # %s 2
            session_id,   # %s 3
            trade_time,   # %s 4
            pay,          # %s 5 (bigint)
            card_num,     # %s 6
            bank_num,     # %s 7
            quantity      # %s 8
        )
        
        DB.execute_input(sql, input_data)