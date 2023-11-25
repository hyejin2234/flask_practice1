from flask import Flask, render_template, request,flash,redirect,url_for,session, jsonify
from database import DBhandler
import hashlib
import sys
application = Flask(__name__)
application.config["SECRET_KEY"]= "thisisoreo"
DB=DBhandler() #database.py에 들어가면 클래스있음 (DB. 이용)
 
@application.route("/") 
def hello():
    return render_template("index.html")

# 1~4
@application.route("/1~4/item_reg")
def view_reg_items():
    return render_template("1~4/item_reg.html")

@application.route("/1~4/view_item")
def view_items():
    return render_template("1~4/view_item.html")

@application.route("/1~4/item_detail")
def view_item_detail():
    return render_template("1~4/item_detail.html")

@application.route("/1~4/order")
def view_item_detai():
    return render_template("1~4/order.html")

@application.route("/order_item")
def view_order_confirmation():
    #구매한후 구매자 포인트 감소
    flash('1000포인트가 차감되었습니다')
    DB.update_point(session['id'], 1000)
    DB.update_ranking_point(session['id'], 1000)
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



#리뷰 데이터 넘겨줌
@application.route("/reg_reviews", methods=['POST'])
def reg_reviews():
    image_file=request.files["chooseFile"]
    image_file.save("static/img/{}".format(image_file.filename))
    data=request.form
    DB.reg_review(data, image_file.filename)
    return redirect(url_for('view_all_review'))

    # 리뷰등록누르면 상품name지정 리뷰작성화면
@application.route("/reg_review_init/<name>/")
def reg_review_init(name):
    info = DB.reference('item')
    info_data = info.child(name).get()
    professor = info_data.get("professor",None)    # 데이터베이스 item에서 교수님정보 가지고옴
    subject = info_data.get("subject",None)        # 과목
    subject_num = info_data.get("subject_id",None)# 학수번호
    reviewer = session['id']
    return render_template("reg_reviews.html", reviewer=reviewer, name=name, subject=subject, professor=professor, subject_num=subject_num)

##@application.route("/reg_review", methods=['POST'])  ## 이게 필요한가?
##def reg_review():
##    data=request.form                                   ## post로 전송한 데이터
##    DB.reg_review(data)                                 ## DB객체의 'reg_review" 메서드 호출하여 등록된 리뷰 db에 등록
##    return redirect(url_for('view_review'))             ##'view_review'라는 함수(또는 라우트)에 대한 URL을 생성하고, 그 URL로 클라이언트의 브라우저를 리디렉션(등록된리뷰가 표시되는 페이지로 이동)


## 이거 커밋!  ## 상품명 가져와서 그 상품에 대한 리뷰만 추출
@application.route("/review_init/<name>/")
def reg_init(name):
    reviews = DB.get_reviews(name)
    tot_count = len(reviews)
    return render_template("review.html", name=name, reviews = reviews.items(), total=tot_count())


##커밋 전체리뷰화면 커밋 이거는 헤더에 리뷰보기
@application.route("/review")     # html 필요
def view_all_review():
    page = request.args.get("page", 0, type=int)
    per_page=6 # item count to display per page
    per_row=1  # item count to display per row
    row_count=int(per_page)
    start_idx=per_page*page
    end_idx=per_page*(page+1)
    data = DB.get_all_reviews()   #데이터베이스에서 리뷰데이터 가져옴
    item_counts = len(data)   # 전체 리뷰의 항목 수
    #tot_count = 0
    #for key, value in data.items():
    #  if isinstance(value, dict):
    #    user_count = len(value)
    #    tot_count += user_count 키값이 두개이므로 반복문 돌면서 "name"에 해당하는 "id"의 개수 더함
    data = dict(list(data.items())[start_idx:end_idx]) #한페이지에 index설정한 개수만큼 읽어오기
    tot_count = len(data)
    for i in range(row_count): #last row_count 
        if (i == row_count-1) and (tot_count%per_row != 0):
            locals()['data_{}'.format(i)] = dict(list(data.items())[i*per_row:])
        else:
            locals()['data_{}'.format(i)] = dict(list(data.items())[i*per_row:(i+1)*per_row])
    return render_template("review.html", datas=data. items(),row1=locals()['data_0'].items(), row2=locals()['data_1'].items(),
                           row3=locals()['data_2'].items(), row4=locals()['data_3'].items(),row5=locals()['data_4'].items(), row6=locals()['data_5'].items(),
                           limit=per_page, page=page, page_count=int((item_counts/per_page)+1), total=item_counts)


## 상픔별 리뷰화면 커밋 -> 상품상세화면에서 리뷰보기 클릭하면 나오는 걸로
@application.route("/review")
def view_review():
    page = request.args.get("page", 0, type=int)
    per_page=6 # item count to display per page
    per_row=1  # item count to display per row
    row_count=int(per_page)
    start_idx=per_page*page
    end_idx=per_page*(page+1)
    data = DB.get_reviews()   #데이터베이스에서 리뷰데이터 가져옴
    item_counts = len(data)   # 전체 리뷰의 항목 수
    data = dict(list(data.items())[start_idx:end_idx])
    tot_count = len(data)
    for i in range(row_count): #last row_count 
        if (i == row_count-1) and (tot_count%per_row != 0):
            locals()['data_{}'.format(i)] = dict(list(data.items())[i*per_row:])
        else:
            locals()['data_{}'.format(i)] = dict(list(data.items())[i*per_row:(i+1)*per_row])
    return render_template("review.html", datas=data. items(),row1=locals()['data_0'].items(), row2=locals()['data_1'].items(),
                           row3=locals()['data_2'].items(), row4=locals()['data_3'].items(),row5=locals()['data_4'].items(), row6=locals()['data_5'].items(),
                           limit=per_page, page=page, page_count=int((item_counts/per_page)+1), total=item_counts)





# 8~10
#회원가입
@application.route("/signup")
def signup():
    return render_template("8~10/signup.html")
@application.route("/signup_post",methods=['POST'])
def register_user():
    data=request.form
    id=request.form['id']
    pw=request.form['pw']
    pw2=request.form['PWconfirm']
    nname=request.form['nickname']
    pw_hash=hashlib.sha256(pw.encode('utf-8')).hexdigest()
    pw_hash2=hashlib.sha3_256(pw.encode('utf-8')).hexdigest()
    #아이디중복확인
    if 'check_duplicate_id' in request.form:
        if DB.id_duplicate_check(id):
            flash('사용할 수 있는 아이디입니다.')
            return render_template("8~10/signup.html")
        else:
            flash('이미 존재하는 아이디입니다.')
            return render_template("8~10/signup.html")

    #닉네임중복확인
    if 'check_duplicate_nickname' in request.form:
        if DB.nickname_duplicate_check(nname):
            flash('사용할 수 있는 닉네임입니다.')
            return render_template("8~10/signup.html")
        else:
            flash('이미 존재하는 닉네임입니다.')
            return render_template("8~10/signup.html")
    if pw!=pw2:
        flash("비밀번호를 확인해주세요")
        return render_template("8~10/signup.html")
    else:
        if DB.insert_user(data,pw_hash,pw_hash2):
            flash("회원가입되었습니다.")
            return render_template("8~10/login.html")
        else:
            flash("중복확인를 눌러주세요")
            return render_template("8~10/signup.html")

    

# 로그인 하기
@application.route("/login")
def login():
    return render_template("8~10/login.html")
@application.route("/login_confirm", methods=['POST'])
def login_user():
    id_=request.form['id']
    pw=request.form['pw']
    pw_hash = hashlib.sha256(pw.encode('utf-8')).hexdigest()
    if DB.find_user(id_,pw_hash):
        session['id']=id_
        return redirect(url_for('hello')) #나중에 전체상품조회로 바꿀예정
    else:
        flash("Wrong ID or PW!")
        return render_template("8~10/login.html")

# 로그아웃
@application.route("/logout")
def logout_user():
    session.clear()
    return redirect(url_for('hello')) #나중에 전체상품조회로 바꿀예정
    



    ################
@application.route("/submit_item_post",methods=['POST'])
def reg_item_submit_post():
    image_file=request.files["file"]
    image_file.save("static/images/{}".format(image_file.filename))
    data = request.form
    return render_template("submit_item_result.html", data=data, img_path="static/images/{}".format(image_file.filename))

if __name__ == "__main__":
    application.run(host='0.0.0.0', debug = True)