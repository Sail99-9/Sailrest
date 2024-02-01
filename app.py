from flask import Flask, render_template, redirect, url_for
app = Flask(__name__)

@app.route("/")
def home():
    return render_template('mainpage.html')

@app.route("/image/")
def image():
    image_url = "https://www.greenart.co.kr/upimage/new_editor/20212/20210201112021.jpg"
    author_url = "https://github.com/Sail99-9/Sailrest"
    author_img_url = "https://velog.velcdn.com/images/heelieben/post/cd5beeed-ba8b-463c-8157-7f0dc803605e/image.png"
    author_id = "hanghae99"
    caption = "내용이 여기 들어갑니다."
    comments = ["댓글1", "댓글2", "댓글3", "댓글4", "댓글5"]

    context = {
        "image_url": image_url,
        "author_url": author_url,
        "author_img_url": author_img_url,
        "author_id": author_id,
        "caption": caption,
        "comments": comments,
    }
    return render_template('imagepage.html', data=context)

if __name__ == "__main__":
    app.run(debug=True)