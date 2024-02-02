from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin, current_user
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key'  # 반드시 시크릿 키를 변경해야 합니다.

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager = LoginManager(app)


@login_manager.user_loader
def load_user(user_id):
    # 사용자 ID를 기반으로 사용자를 식별하여 반환하는 로직을 구현
    return User.query.get(user_id)


class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

    def get_id(self):
        return str(self.id)


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
    user_id = db.Column(db.String, nullable=False)
    # order = db.Column(db.Integer, primary_key=True, nullable=False)
    comment = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime, primary_key=False)


class PinImage(db.Model):
    pin_id = db.Column(db.Integer, primary_key=True)
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
    image_data = Image.query.with_entities(
        Image.image_id, Image.image_url).all()
    return render_template('mainpage.html', image_data=image_data)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        now = datetime.now()
        date = datetime.fromtimestamp(now.timestamp()).strftime('%Y%m%d%H%M%S')
        id = ''.join((password, date))
        new_user = User(username=username, password=password, id=id)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('mainpage'))
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        next = request.args.get('next', url_for('mainpage_login'))
    else:
        # form 방식으로 받아올 때에는 form에, json 방식으로 받아올 때에는 json에 원하는 정보가 담겨있음
        user_id = request.form.get('username')
        password = request.form.get('password')
        next = request.form.get('next')
        safe_next_redirect = url_for('mainpage')
        if next:
            safe_next_redirect = next
        user = User.query.filter_by(username=user_id).first()
        print(password)
        if user and user.password == password:
            # login 한 사용자의 정보를 session에 저장해줌
            login_user(user)
            return redirect(safe_next_redirect)
        else:
            # 로그인 실패 시
            return render_template('alert.html', messages="회원정보가 틀렸습니다.")
    return redirect(safe_next_redirect)


@app.route('/logout')
@login_required
def logout():
    session.clear()  # 세션 정보 초기화
    logout_user()
    return redirect(url_for('mainpage'))


@login_required
@app.route('/mypage/<username>')
def mypage(username):
    image_data = Image.query.filter_by(author_id=current_user.username).with_entities(
        Image.image_id, Image.image_url).all()
    return render_template('mypage.html', image_data=image_data, username=username)


@app.route("/image/<image_id>/")
def image(image_id):
    image = Image.query.filter_by(image_id=image_id).all()
    comments = Comment.query.filter_by(image_id=image_id).all()
    context = {
        "image": image,
        "comments": comments,
    }
    return render_template('imagepage.html', data=context)


@app.route('/comment/write/')
@login_required
def comment_write():
    # user_id 없이 comment만 DB저장하는 방법
    comment_receive = request.args.get("comment")
    image_id = request.args.get("image_id")
    user_id = current_user.username
    now = datetime.now()
    created_at_time = now
    comment_data = Comment(
        image_id=image_id,user_id=user_id, comment=comment_receive, created_at=created_at_time)
    db.session.add(comment_data)
    db.session.commit()
    return redirect(url_for('image', image_id=image_id))


@app.route('/image/<image_id>/pined/')
def pin_image(image_id):
    user_id = "hsm"  # 로그인 정보 받아와야 함
    now = datetime.now()
    created_at_time = now
    pin_image = PinImage(image_id=image_id, user_id=user_id,
                         created_at=created_at_time)
    db.session.add(pin_image)
    db.session.commit()
    return render_template('mypage.html', username=user_id)


@app.route("/image/uploadPage/")
def image_upload_page():
    return render_template('imageUpload.html')


@app.route("/image/upload/")
@login_required
def image_upload():
    # form 정보 받아오기
    image_receive = request.args.get("image")
    image_url_receive = request.args.get("imageInput")
    title_receive = request.args.get("imageName")
    caption_receive = request.args.get("imageCaption")
    author_id_receive = current_user.username
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
    # 나머지 이미지 정보 생성하기
    now = datetime.now()
    created_at_time = now
    image_id_date = datetime.fromtimestamp(
        now.timestamp()).strftime('%Y%m%d%H%M%S')
    image_id_create = ''.join((author_id_receive, image_id_date))
    pined_create = 0
    # 데이터를 db에 저장하기
    image = Image(image_id=image_id_create, author_id=author_id_receive, title=title_receive,
                  caption=caption_receive, pined=pined_create, image_url=image_info, created_at=created_at_time)
    db.session.add(image)
    db.session.commit()
    return redirect(url_for('mainpage'))


if __name__ == '__main__':
    app.run(debug=True)
