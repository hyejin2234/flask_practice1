from flask import Flask, render_template, request 
from database import DBhandler
import sys
application = Flask(__name__)

DB = DBhandler()
 
@application.route("/") 
def hello():
    return render_template("index.html")

@application.route("/index")
def comback_home():
    return render_template("index.html")

# 1~4
@application.route("/1~4/1")
def view_reg_items():
    return render_template("1~4/1.html")

@application.route("/1~4/2")
def view_items():
    return render_template("1~4/2.html")

@application.route("/1~4/3")
def view_item_detail():
    return render_template("1~4/3.html")

@application.route("/1~4/4")
def view_order_confirmation():
    return render_template("1~4/4.html")

# 5~7
@application.route("/5-7/reg_reviews")
def view_reg_review():
    return render_template("5-7/reg_reviews.html")

@application.route("/5-7/review")
def view_reviews():
    return render_template("5-7/review.html")

@application.route("/5-7/review_detail")
def view_review_detail():
    return render_template("5-7/review_detail.html")

@application.route("/submit_review_post", methods=['POST'])  ##이것도 커밋
def reg_review_submit_post():
    image_file=request.files["chooseFile"]                  
    image_file.save("static/images/{}".format(image_file.filename))
    data=request.form                                       ## form데이터에서 전송된 모든 데이터를 data에 저장 
    DB.reg_review(data['키값'], data, image_file.filename)  ##data['name']에서 name으로 들어오는게 없는데 이거 수정필요! #데이터에 리뷰정보등록

    return render_template("전체리뷰화면.html", data=data,img_path="static/images/{}".format(image_file.filename))  ## 어떤 html로 이 정보보내서 렌더링할지 


@application.route("/reg_review_init/<name>/")  ## 이거 커밋!
def reg_review_init(name):                      ## 리뷰등록누르면 name지정되서 리뷰작성화면으로 고고
    return render_template("reg_reviews.html", name=name)

##@application.route("/reg_review", methods=['POST'])  ## 이게 필요한가? 커밋! 
##def reg_review():
##    data=request.form                                   ## post로 전송한 데이터
##    DB.reg_review(data)                                 ## DB객체의 'reg_review" 메서드 호출하여 등록된 리뷰 db에 등록
##    return redirect(url_for('view_review'))             ##'view_review'라는 함수(또는 라우트)에 대한 URL을 생성하고, 그 URL로 클라이언트의 브라우저를 리디렉션(등록된 리뷰가 표시되는 페이지로 이동)


# 8~10
@application.route("/8~10/signup")
def view_signup():
    return render_template("8~10/signup.html")

@application.route("/8~10/login")
def view_login():
    return render_template("8~10/login.html")

@application.route("/8~10/ranking")
def view_ranking():
    return render_template("8~10/ranking.html")

@application.route("/submit_item")
def reg_item_submit():
    name=request.args.get("name")
    seller=request.args.get("seller")
    addr=request.args.get("addr")
    email=request.args.get("email")
    category=request.args.get("category")
    card=request.args.get("card")
    status=request.args.get("status")
    phone=request.args.get("phone")
    
    print(name,seller,addr,email,category,card,status,phone) 
    #return render_template("reg_item.html")
    
@application.route("/submit_item_post",methods=['POST'])
def reg_item_submit_post():
    image_file=request.files["file"]
    image_file.save("static/images/{}".format(image_file.filename))
    data = request.form
    return render_template("submit_item_result.html", data=data, img_path="static/images/{}".format(image_file.filename))

if __name__ == "__main__":
    application.run(host='0.0.0.0', debug = True)