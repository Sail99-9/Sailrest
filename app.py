from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key'  # 반드시 시크릿 키를 변경해야 합니다.

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

class Image(db.Model):
    image_id = db.Column(db.String, primary_key=True)
    author_id = db.Column(db.String, primary_key=False)
    title = db.Column(db.String, primary_key=False)
    caption = db.Column(db.String, primary_key=False)
    pined = db.Column(db.Integer, primary_key=False)
    image_url = db.Column(db.String, primary_key=False)
    created_at = db.Column(db.DateTime, primary_key=False)

class Comment(db.Model):
    comment_id = db.Column(db.Integer, primary_key=True)
    image_id = db.Column(db.String, nullable=False)
    # user_id = db.Column(db.String, nullable=False)
    # order = db.Column(db.Integer, primary_key=True, nullable=False)
    comment = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime, primary_key=False)

class PinImage(db.Model):
    pid_id = db.Column(db.Integer, primary_key=True)
    image_id = db.Column(db.String, nullable=False)
    user_id = db.Column(db.String)
    created_at = db.Column(db.DateTime, primary_key=False)


# 데이터베이스 초기화를 애플리케이션이 실행될 때 수행
def create_tables():
    with app.app_context():
        db.create_all()

# create_tables 함수를 호출하여 데이터베이스 초기화
create_tables()

@app.route('/', methods=['GET', 'POST'])
def mainpage():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()

        if User.query.filter_by(password=password).first():
            session['user_id'] = user.id
            return redirect(url_for('login', username=username))

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

@app.route('/login/<username>')
def login(username):
    return render_template('mainpage_login.html', username=username)

@app.route('/mypage/<username>')
def mypage(username):
    return render_template('mypage.html', username=username)

@app.route("/image/<image_id>/")
def image(image_id):
    image = Image.query.filter_by(image_id=image_id).all()
    author_img_url = "https://velog.velcdn.com/images/heelieben/post/cd5beeed-ba8b-463c-8157-7f0dc803605e/image.png"
    comments = Comment.query.filter_by(image_id=image_id).all()

    context = {
        "author_img_url": author_img_url,
        "image": image,
        "comments": comments,
    }
    return render_template('imagepage.html', data=context)

@app.route('/comment/write/')
def comment_write():
    # user_id 없이 comment만 DB저장하는 방벙
    comment_receive = request.args.get("comment")
    image_id = request.args.get("image_id")

    now = datetime.now()
    created_at_time=now

    # comment_data = Comment(comment_id=comment_id, image_id=image_id, user_id=user_id, order=order, comment=comment_receive, created_at=created_at_time)

    # db.session.add()
    # db.session.commit()

    return redirect(url_for('image', image_id=image_id))

@app.route('/image/pined/')
def pin_image():
    username = "hsm"
    # DB 해당 이미지 pined 항목 수정
    return redirect(url_for('mypage', username=username))

@app.route("/image/uploadPage/")
def image_upload_page():
    return render_template('imageUpload.html')

@app.route("/image/upload/")
def image_upload():
    #form 정보 받아오기
    image_receive=request.args.get("image")
    image_url_receive=request.args.get("imageUrl")
    title_receive=request.args.get("imageName")
    caption_receive=request.args.get("imageCaption")
    author_id_receive="uha"

    if image_receive is not None and image_url_receive is None:
        image_info = image_receive
    elif image_receive is None and image_url_receive is not None:
        image_info = image_url_receive
    elif image_receive is not None and image_url_receive is not None:
        messages = '이미지나 URL 중 하나를 입력해 주세요'
        return render_template('alert.html', messages=messages)
    else:
        messages = '이미지나 URL을 입력해 주세요'
        return render_template('alert.html', messages=messages)


    #나머지 이미지 정보 생성하기
    now = datetime.now()
    created_at_time=now
    image_id_date=datetime.fromtimestamp(now.timestamp()).strftime('%Y%m%d%H%M%S')
    image_id_create=''.join((author_id_receive,image_id_date))
    pined_create=0

    #데이터를 db에 저장하기
    image = Image(image_id=image_id_create,author_id=author_id_receive,title=title_receive,caption=caption_receive,pined=pined_create,image_url=image_info,created_at=created_at_time)
    db.session.add(image)
    db.session.commit()
    return redirect(url_for('mainpage'))

if __name__ == '__main__':
    app.run(debug=True)