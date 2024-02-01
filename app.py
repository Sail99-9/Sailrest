from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key'  # 반드시 시크릿 키를 변경해야 합니다.

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

# 데이터베이스 초기화를 애플리케이션이 실행될 때 수행
def create_tables():
    with app.app_context():
        db.create_all()

# create_tables 함수를 호출하여 데이터베이스 초기화
create_tables()

@app.route('/', methods=['GET', 'POST'])
def mainpage():
    login_success = False
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()

        if User.query.filter_by(password=password).first():
            session['user_id'] = user.id
            return redirect(url_for('login'))

    return render_template('mainpage.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('mainpage'))

    return render_template('register.html')

@app.route('/login')
def login():
    return render_template('mainpage_login.html')

@app.route('/mypage')
def mypage():
    return render_template('mypage.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('mainpage'))

if __name__ == '__main__':
    app.run(debug=True)