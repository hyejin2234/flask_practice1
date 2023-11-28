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
    if 'id' not in session or not session['id']:
        flash('리뷰를 작성하려면 로그인을 해주세요.')
        return redirect(url_for('login'))
    else:
        return render_template("5-7/reg_reviews.html")


#@application.route("/5-7/review_detail")
#def view_review_detail():
#    return render_template("5-7/review_detail.html")


#리뷰 데이터 넘겨줌
@application.route("/reg_reviews", methods=['POST'])
def reg_reviews():
    data=request.form
    user_id = session.get('id')
    image_file = request.files["chooseFile"]
    if image_file:
        image_file.save("static/img/{}".format(image_file.filename))
        DB.reg_review(data, user_id, image_file.filename)
    else:
        # image_file이 없는 경우에는 사진 빼고 등록
        DB.reg_review(data, user_id, None)
    return redirect(url_for('view_all_review'))

#리뷰작성화면
@application.route("/reg_review_init/<name>/")
def reg_review_init(name):
    if 'id' not in session or not session['id']:
        flash('리뷰를 작성하려면 로그인을 해주세요.')
        return redirect(url_for('login'))
    else:
        info = DB.reference('item')
        info_data = info.child(name).get()
        #판매자정보추가
        professor = info_data.get("professor",None)
        subject = info_data.get("subject",None)
        subject_id = info_data.get("subject_id",None)
        reviewer = session['id']
        return render_template("5-7/reg_reviews.html", reviewer=reviewer, name=name, subject=subject, professor=professor, subject_id=subject_id)


## 이거 커밋!  ## 상품명 가져와서 그 상품에 대한 리뷰만 추출
#@application.route("/review_init/<name>/")
#def reg_init(name):
    #reviews = DB.get_reviews(name)
    #tot_count = len(reviews)
    #return render_template("review.html", name=name, reviews = reviews.items(), total=tot_count())


## 전체리뷰화면 -> 헤더에 리뷰보기
@application.route("/5-7/review")     # html 필요
def view_all_review():
    page = request.args.get("page", 0, type=int)
    per_page=6 # 한페이지에 리뷰 6개
    per_row=1  # 1줄에 하나씩
    row_count=int(per_page) #한페이지에 표시할 행 개수(6개)
    start_idx=per_page*page #현재페이지에 보여줄 리뷰의 시작인덱스
    end_idx=per_page*(page+1) #현재페이지에 보여줄 리뷰의 끝 인덱스

    data = DB.get_all_reviews()
    #전체 리뷰의 개수 계산
    item_counts = len(data)
    #현재페이지에 보여줄 리뷰들만 읽어오기
    data = dict(list(data.items())[start_idx:end_idx]) 
    #현재페이지에서 실제로 보여지는 개수
    tot_count = len(data)
    for i in range(row_count): #행 개수만큼 반복(6번)
        if (i == row_count-1): #마지막 행일 경우
            locals()['data_{}'.format(i)] = dict(list(data.items())[i*per_row:])
        else: #마지막 행이 아닌 경우
            locals()['data_{}'.format(i)] = dict(list(data.items())[i*per_row:(i+1)*per_row])
    return render_template("/5-7/review.html", datas=data.items(), row1=locals()['data_0'].items(), row2=locals()['data_1'].items(),
                           row3=locals()['data_2'].items(), row4=locals()['data_3'].items(),row5=locals()['data_4'].items(), row6=locals()['data_5'].items(),
                           limit=per_page, page=page, page_count=int((item_counts/per_page)+1), total=item_counts)


##상픔별 리뷰화면 -> 상품상세화면에서 리뷰보기 클릭하면 나오는 걸로
@application.route("/review/<name>/")
def view_review():
    page = request.args.get("page", 0, type=int)
    per_page=6 # 한페이지에 리뷰 6개
    per_row=1  # 1줄에 하나씩
    row_count=int(per_page) #한페이지에 표시할 행 개수(6개)
    start_idx=per_page*page #현재페이지에 보여줄 리뷰의 시작인덱스
    end_idx=per_page*(page+1) #현재페이지에 보여줄 리뷰의 끝 인덱스
    data = DB.get_reviews(str(name))
    
    #전체 리뷰의 개수 계산
    item_counts = len(data)
    
    #모든 리뷰의 별의 합을 구하고 리뷰 개수로 나누어 평균별점 계산
    total_star = sum(int(data['rate']) for i in data.values())
    average_star = total_star/item_counts
    
    #각 키워드에 개수 구해서 %계산
    keyword1=0
    keyword2=0
    keyword3=0
    for i in data.values():
        if i.get('keyword')=='자세한설명':
            keyword1 =  keyword1+1
        elif i.get('keyword')=='핵심위주':
            keyword2 =  keyword2+1
        elif i.get('keyword')=='문제풀이':
            keyword3 =  keyword3+1
    proportion_1 = keyword1/item_counts*100
    proportion_2 = keyword2/item_counts*100
    proportion_3 = keyword3/item_counts*100
            
    #현재 페이지에 보여줄 리뷰만 추출
    data = dict(list(data.items())[start_idx:end_idx])

    for i in range(row_count):
        if (i == row_count-1): #마지막 row
            locals()['data_{}'.format(i)] = dict(list(data.items())[i*per_row:])
        else:
            locals()['data_{}'.format(i)] = dict(list(data.items())[i*per_row:(i+1)*per_row])
    return render_template("review.html", datas=data. items(),row1=locals()['data_0'].items(), row2=locals()['data_1'].items(),
                           row3=locals()['data_2'].items(), row4=locals()['data_3'].items(),row5=locals()['data_4'].items(), row6=locals()['data_5'].items(),
                           limit=per_page, page=page, page_count=int((item_counts/per_page)+1), total=item_counts, average_star=average_star, proportion_1=proportion_1, proportion_2=proportion_2, proportion_3=proportion_3)

#리뷰상세페이지
@application.route("/view_review_detail/<name>/")
def view_review_detail(name):
    print("###name:",name)
    data = DB.get_item_byname(str(name))
    print("####data:",data)
    return render_template("review_detail.html", name=name, data=data)



# 8~10
#회원가입
@application.route("/8-10/signup")
def signup():
    return render_template("8-10/signup.html")
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
            return render_template("8-10/signup.html")
        else:
            flash('이미 존재하는 아이디입니다.')
            return render_template("8-10/signup.html")

    #닉네임중복확인
    if 'check_duplicate_nickname' in request.form:
        if DB.nickname_duplicate_check(nname):
            flash('사용할 수 있는 닉네임입니다.')
            return render_template("8-10/signup.html")
        else:
            flash('이미 존재하는 닉네임입니다.')
            return render_template("8-10/signup.html")
    if pw!=pw2:
        flash("비밀번호를 확인해주세요")
        return render_template("8-10/signup.html")
    else:
        if DB.insert_user(data,pw_hash,pw_hash2):
            flash("회원가입되었습니다.")
            return render_template("8-10/login.html")
        else:
            flash("중복확인를 눌러주세요")
            return render_template("8-10/signup.html")

    

# 로그인 하기
@application.route("/8-10/login")
def login():
    return render_template("/8-10/login.html")
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
        return render_template("8-10/login.html")

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