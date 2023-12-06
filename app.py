from flask import Flask, render_template, request,flash,redirect,url_for,session, jsonify
from database import DBhandler
import hashlib
import sys
import math
application = Flask(__name__)
application.config["SECRET_KEY"]= "thisisoreo"
DB=DBhandler() #database.py에 들어가면 클래스있음 (DB. 이용)

@application.route("/") 
def hello():
    return render_template("index.html")
    #return redirect(url_for('view_items'))

@application.route("/index")
def comback_home():
    return render_template("index.html")

# 1~4
@application.route("/1-4/item_reg")
def view_reg_items():
    if 'id' not in session or not session['id']:
            flash('상품을 등록하려면 로그인을 해주세요.')
            return redirect(url_for('login'))
    else:
            return render_template("1-4/item_reg.html")

# item_reg.html에서 입력한 값 get하기
@application.route("/submit_item")
def reg_item_submit():
    item_name=request.args.get("item_name")
    item_type=request.args.get("item_type")
    price=request.args.get("price")

    #print(item_name, item_type, price)


# item_reg.html에서 입력한 값 db에 저장하고 결과 화면으로 넘겨주기
@application.route("/submit_item_post", methods=['POST'])
def reg_item_submit_post():

    if 'id' not in session or not session['id']:
        flash('리뷰를 작성하려면 로그인을 해주세요.')
        return redirect(url_for('login'))
    else:
        item_file=request.files['item_upload']
        item_file.save("static/items/{}".format(item_file.filename))
        photo_file=request.files.getlist("photo_upload[]")
        data=request.form
        writer = session['id']

        print( 'before db insertion' )
        
        for f in photo_file:
            f.save('static/photos/' + f.filename)

        DB.insert_item(data['item_name'], data, item_file.filename, [f.filename for f in photo_file], session['id'])
    
        print( 'after db insertion' )

        return render_template("1-4/item_detail.html", data=data, item_path="static/items/{}".format(item_file.filename), photo_paths=["static/photos/{}".format(f.filename) for f in photo_file])



#### 맨 처음 화면이 이 view_items()함수로 옴.
@application.route("/1-4/view_item")
def view_items():
    page = request.args.get("page", 0, type=int)
    per_page=5 # item count to display per page
    per_row=1 # item count to display per row
    major =request.args.get("major","")
    coursetype =request.args.get("course-type","")

    row_count=int(per_page/per_row)
    start_idx=per_page*page
    end_idx=per_page*(page+1)

    if major == "" and coursetype == "":
        data = DB.get_items()  # 모든 아이템 조회
    elif major != "" and coursetype == "":
        data = DB.get_items_bymajor(major)
    elif major == "" and coursetype != "":
        data = DB.get_items_bycoursetype(coursetype)
    else:
        data = DB.get_items_bymajor_coursetype(major, coursetype)
    
    data = DB.get_items()
    item_counts = len(data)
    data = dict(sorted(data.items(), key=lambda x: x[0], reverse=False))
    tot_count = len(data)

    for i in range(row_count): #last row
        if (i == row_count-1) and (tot_count%per_row != 0):
            locals()['data_{}'.format(i)] = dict(list(data.items())[i*per_row:])
        else: 
            locals()['data_{}'.format(i)] = dict(list(data.items())[i*per_row:(i+1)*per_row])

    return render_template("1-4/view_item.html", datas=data.items(), row1=locals()['data_0'].items(), row2=locals()['data_1'].items(), 
                           limit=per_page, page=page, page_count=int((item_counts/per_page) +1), total = item_counts,major=major)


#전체 리스트에서 상품 클릭 시 세부정보 볼 수 있음
@application.route("/1-4/view_item_detail/<item_name>/")
def view_item_detail(item_name):
    print("###name:", item_name)
    data=DB.get_item_byname(str(item_name))
    print("####data:",data)
    return render_template("1-4/detail.html", item_name=item_name, data=data)


#좋아요 관련 기능
@application.route('/show_heart/<item_name>/', methods=['GET'])
def show_heart(item_name):
    if 'id' not in session or not session['id']:
        flash('상품을 찜하려면 로그인을 해주세요.')
        return redirect(url_for('login'))
    else:
        my_heart = DB.get_heart_byname(session['id'],item_name)
        return jsonify({'my_heart': my_heart})
 
@application.route('/like/<item_name>/', methods=['POST'])
def like(item_name):
    if 'id' not in session or not session['id']:
        flash('상품을 찜하려면 로그인을 해주세요.')
        return redirect(url_for('login'))
    else:
        my_heart = DB.update_heart(session['id'],'Y',item_name)
        return jsonify({'msg': '좋아요 완료!'})

@application.route('/unlike/<item_name>/', methods=['POST'])
def unlike(item_name):
    if 'id' not in session or not session['id']:
        flash('상품을 찜하려면 로그인을 해주세요.')
        return redirect(url_for('login'))
    else:
        my_heart = DB.update_heart(session['id'],'N',item_name)
        return jsonify({'msg': '안좋아요 완료!'})
####### likes ########


@application.route("/1-4/order_item")
def order_item():
    return render_template("1~4/order_item.html")



#구매하기 버튼 누르면
@application.route("/1-4/order_item/<item_name>/")
def view_order_confirmation(item_name):

    point=DB.get_price(str(item_name))
    seller=DB.get_seller(str(item_name))

    if 'id' not in session or not session['id']:
        flash('구매하시려면 로그인을 해주세요.')
        return redirect(url_for('login'))
    else:

        download_count = DB.increase_download_count(item_name) #다운로드 횟수 증가

        DB.update_point(session['id'], point) #구매자 포인트 감소
        DB.update_ranking_point(session['id'], point) #구매자 랭킹 포인트 증가
        DB.update_point_2(seller,point) #판매자 포인트 증가
        DB.update_ranking_point(seller,point) #판매자 랭킹 포인트 증가
        
        DB.insert_purchase_history(item_name, session['id'])
        seller_email = DB.get_seller_email(item_name)

        flash('포인트가 차감되었습니다')

        data=DB.get_item_byname(str(item_name))
        session['user_point'] = DB.get_user_point(session['id'])

    return render_template("1-4/order_item.html", data=data, item_name=item_name, seller_email=seller_email, download_count=download_count)


# 5~7
# 리뷰작성 -> 구매내역페이지
@application.route("/5-7/reg_reviews")
def view_reg_review():
    if 'id' not in session or not session['id']:
        flash('리뷰를 작성하려면 로그인을 해주세요.')
        return redirect(url_for('login'))
    else:
        #return render_template("5~7/reg_reviews.html")
        page = request.args.get("page", 0, type=int)
        per_page=6
        per_row=1
        row_count=int(per_page)
        start_idx=per_page*page
        end_idx=per_page*(page+1)

        purchase = DB.get_purchase_history(session['id'])        #구매내역 불러오기
        if purchase == None:                                     #구매내역
            total=0
            return render_template("/5-7/mypage.html",total=total)
        else:
            item_counts = len(purchase)
            purchase = dict(list(purchase.items())[start_idx:end_idx])
            keys = purchase.keys() #해당 key=상품이름
            for key in keys:
                item_info = DB.get_item_byname(key)
                purchase[key]["item_name"]=item_info.get("item_name")
                purchase[key]["writer"]=item_info.get("writer")
                purchase[key]["photo_path"]=item_info.get("photo_path")

            tot_count = len(purchase)
            for i in range(row_count):
                if (i == row_count-1):
                    locals()['data_{}'.format(i)] = dict(list(purchase.items())[i*per_row:])
                else:
                    locals()['data_{}'.format(i)] = dict(list(purchase.items())[i*per_row:(i+1)*per_row])
            return render_template("/5~7/mypage.html", purchase=purchase.items(), row1=locals()['data_0'].items(), row2=locals()['data_1'].items(),
                           row3=locals()['data_2'].items(), row4=locals()['data_3'].items(),row5=locals()['data_4'].items(), row6=locals()['data_5'].items(),
                           limit=per_page, page=page, page_count=int((item_counts/per_page)+1), total=item_counts)

                #if len(locals()['data_{}'.format(i)])>0:
                    #item_name = locals()['data_{}'.format(i)][session['id']]["item_name"]                      #해당 purchase.items()의 이름 가지고 와서
                    #item_info = DB.get_item_byname(item_name)                                   #그 아이템의 정보 불러옴
                    #locals()['data_{}'.format(i)][session['id']]["item_name"] = item_info.get("item_name")
                    #locals()['data_{}'.format(i)][session['id']]["professor"] = item_info.get("professor")
                    #locals()['data_{}'.format(i)][session['id']]["course_name"] = item_info.get("course_name")
                    #locals()['data_{}'.format(i)][session['id']]["course_number"] = item_info.get("course_number")
                    #locals()['data_{}'.format(i)][session['id']]["writer"] = item_info.get("writer")
                    #locals()['data_{}'.format(i)][session['id']]["photo_path"] = item_info.get("photo_path")


#상품이름 가지고 와서 리뷰작성페이지
@application.route("/reg_review_init/<name>/")
def reg_review_init(name):
    if 'id' not in session or not session['id']:
        flash('리뷰를 작성하려면 로그인을 해주세요.')
        return redirect(url_for('login'))
    else:
        info = DB.get_item_byname(name)
        item_name = info.get("item_name")
        professor = info.get("professor",None)
        subject = info.get("course_number",None)
        writer = info.get("writer",None)
        reviewer = session['id']
        return render_template("5-7/reg_reviews.html", writer=writer, item_name = item_name, reviewer=reviewer, professor=professor,subject=subject)

#작성된 리뷰 데이터 넘겨줌
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

#전체리뷰화면
# @application.route("/5~7/review")     # html 필요
# def view_all_review():
#     page = request.args.get("page", 0, type=int)
#     per_page=6 # 한페이지에 리뷰 6개
#     per_row=1  # 1줄에 하나씩
#     row_count=int(per_page) #한페이지에 표시할 행 개수(6개)
#     start_idx=per_page*page #현재페이지에 보여줄 리뷰의 시작인덱스
#     end_idx=per_page*(page+1) #현재페이지에 보여줄 리뷰의 끝 인덱스
    
#     data = DB.get_all_reviews()
#     #전체 리뷰의 개수 계산
#     item_counts = len(data)
#     #현재페이지에 보여줄 리뷰들만 읽어오기
#     data = dict(list(data.items())[start_idx:end_idx]) 
#     #현재페이지에서 실제로 보여지는 개수
#     tot_count = len(data)
#     for i in range(row_count): #행 개수만큼 반복(6번)
#         if (i == row_count-1): #마지막 행일 경우
#             locals()['data_{}'.format(i)] = dict(list(data.items())[i*per_row:])
#         else: #마지막 행이 아닌 경우
#             locals()['data_{}'.format(i)] = dict(list(data.items())[i*per_row:(i+1)*per_row])
#     return render_template("/5~7/review.html", datas=data.items(), row1=locals()['data_0'].items(), row2=locals()['data_1'].items(),
#                            row3=locals()['data_2'].items(), row4=locals()['data_3'].items(),row5=locals()['data_4'].items(), row6=locals()['data_5'].items(),
#                            limit=per_page, page=page, page_count=int((item_counts/per_page)+1), total=item_counts)

#상품별리뷰페이지
@application.route("/review/<name>/")
def view_review(name):
    page = request.args.get("page", 0, type=int)
    category = request.args.get("category", "all")
    per_page=5 
    per_row=1 
    row_count=int(per_page)
    start_idx=per_page*page
    end_idx=per_page*(page+1)
    #data = DB.get_reviews(str(name))
    if category=="all":
        data = DB.get_reviews(str(name)) #read the table
    else:
        data = DB.get_reviews_bycategory(str(name),category)
    data = dict(sorted(data.items(), key=lambda x: x[0], reverse=False))
    
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
    #data = dict(list(data.items())[start_idx:end_idx])
    if item_counts<=per_page:
        data = dict(list(data.items())[:item_counts])
    else:
        data = dict(list(data.items())[start_idx:end_idx])

    for i in range(row_count):
        if (i == row_count-1): #마지막 row
            locals()['data_{}'.format(i)] = dict(list(data.items())[i*per_row:])
        else:
            locals()['data_{}'.format(i)] = dict(list(data.items())[i*per_row:(i+1)*per_row])
    return render_template("review.html", datas=data. items(),row1=locals()['data_0'].items(), row2=locals()['data_1'].items(),
                           row3=locals()['data_2'].items(), row4=locals()['data_3'].items(),row5=locals()['data_4'].items(),
                           limit=per_page, page=page, page_count=int(math.ceil(item_counts/per_page)), total=item_counts, category=category, average_star=average_star, proportion_1=proportion_1, proportion_2=proportion_2, proportion_3=proportion_3)


#싱세리뷰페이지
@application.route("/view_review_detail/<name>/")
def view_review_detail(name):
    print("###name:",name)
    data = DB.get_review_byname(str(name))
    print("####data:",data)
    return render_template("review_detail.html", name=name, data=data)


#마이페이지 html작업을 위해서 임시로 만들어놓음   
@application.route("/5-7/mypage")
def mypage():
    if 'id' not in session or not session['id']:
        flash('마이페이지에 접근하려면 로그인을 해주세요.')
        return redirect(url_for('login'))
    else:
        datas = DB.get_purchase_history(session['id'])
        print(datas)
    
        return render_template("5-7/mypage.html", datas=datas)

# 8~10

#회원가입
@application.route("/signup")
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
    session['id_'] = id
    session['pw']=pw
    session['pw2']=pw2
    session['nickname']=nname
    session['email']=request.form['email']
    session['HP']=request.form['HP']
    session['college']=request.form['dropdown1']
    session['major']=request.form['dropdown2']
    #아이디중복확인
    if 'check_duplicate_id' in request.form:
        if DB.id_duplicate_check(id):
            flash('사용할 수 있는 아이디입니다.')
            return render_template("8-10/signup.html",
            id=session.get('id_', ''),pw=session.get('pw',''),nickname=session.get('nickname',''),hp=session.get('HP',''),pw2=session.get('pw2',''),
            email=session.get('email',''),college=session.get('college',''),major=session.get('major',''))
        else:
            flash('이미 존재하는 아이디입니다.')
            return render_template("8-10/signup.html",
            id=session.get('id_', ''),pw=session.get('pw',''),nickname=session.get('nickname',''),hp=session.get('HP',''),pw2=session.get('pw2',''),
            email=session.get('email',''),college=session.get('college',''),major=session.get('major',''))

    #닉네임중복확인
    if 'check_duplicate_nickname' in request.form:
        if DB.nickname_duplicate_check(nname):
            flash('사용할 수 있는 닉네임입니다.')
            return render_template("8-10/signup.html",
            id=session.get('id_', ''),pw=session.get('pw',''),nickname=session.get('nickname',''),hp=session.get('HP',''),pw2=session.get('pw2',''),
            email=session.get('email',''),college=session.get('college',''),major=session.get('major',''))
        else:
            flash('이미 존재하는 닉네임입니다.')
            return render_template("8-10/signup.html",
            id=session.get('id_', ''),pw=session.get('pw',''),nickname=session.get('nickname',''),hp=session.get('HP',''),pw2=session.get('pw2',''),
            email=session.get('email',''),college=session.get('college',''),major=session.get('major',''))
    if 'check_same_pw' in request.form:
        if pw!=pw2:
            flash("비밀번호가 불일치합니다")
            return render_template("8-10/signup.html",
                id=session.get('id_', ''),nickname=session.get('nickname',''),hp=session.get('HP',''),
                email=session.get('email',''),college=session.get('college',''),major=session.get('major',''))
        else: 
            flash("비밀번호가 일치합니다")
            return render_template("8-10/signup.html",
                id=session.get('id_', ''),pw=session.get('pw',''),nickname=session.get('nickname',''),hp=session.get('HP',''),pw2=session.get('pw2',''),
                email=session.get('email',''),college=session.get('college',''),major=session.get('major',''))
    
    if DB.insert_user(data,pw_hash,pw_hash2):
        flash("회원가입되었습니다.")
        return render_template("8~10/login.html")
    else:
        flash("입력된 정보를 다시 확인해주세요")
        return render_template("8-10/signup.html",
        id=session.get('id_', ''),pw=session.get('pw',''),nickname=session.get('nickname',''),hp=session.get('HP',''),pw2=session.get('pw2',''),
        email=session.get('email',''),college=session.get('college',''),major=session.get('major',''))

    

# 로그인 하기
@application.route("/login")
def login():
    return render_template("8-10/login.html")
@application.route("/login_confirm", methods=['POST'])
def login_user():
    id_=request.form['id']
    pw=request.form['pw']
    pw_hash = hashlib.sha256(pw.encode('utf-8')).hexdigest()
    if DB.find_user(id_,pw_hash):
        session['id']=id_
        session['user_point'] = DB.get_user_point(session['id'])
        return redirect(url_for('hello')) #나중에 전체상품조회로 바꿀예정
    else:
        flash("Wrong ID or PW!")
        return render_template("8-10/login.html")

# 로그아웃
@application.route("/logout")
def logout_user():
    session.clear()
    return redirect(url_for('hello')) #나중에 전체상품조회로 바꿀예정
    
#랭킹
@application.route("/ranking")
def ranking():
    page = request.args.get("page", 0, type=int)
    per_page=int(10) 
    per_row=int (1) 
    college = request.args.get("category", "all")
    row_count=int(per_page/per_row)
    start_idx=per_page*page
    end_idx=per_page*(page+1)

    if college=="all":
        data = DB.get_users() #전체상품조회 그대로
    else:
        data = DB.get_items_bycollege(college)
    data = dict(sorted(data.items(), key=lambda x: x[1]['rankingpoint'], reverse=True))
    item_counts = len(data)
    if item_counts<=per_page:
        data = dict(list(data.items())[:item_counts])
    else:
        data = dict(list(data.items())[start_idx:end_idx])
    tot_count = len(data)
    for i in range(row_count): 
        if (i == row_count-1) and (tot_count%per_row != 0):
            locals()['data_{}'.format(i)] = dict(list(data.items())[i*per_row:])
        else: 
            locals()['data_{}'.format(i)] = dict(list(data.items())[i*per_row:(i+1)*per_row])
    
    if 'id' in session:
        user_id = session['id']  
        user_ranking_point=DB.get_user_ranking_point(user_id)
    else: 
        user_ranking_point=0
    
    locals()['data_{}'.format(0)] = dict(list(data.items())[0:])

    return render_template(
            "8-10/ranking.html",
            datas=data.items(),
            row=locals()['data_0'].items(),
            limit=per_page,
            page=page,
            page_count=int(math.ceil(item_counts/per_page)), #import math 추가,
            total=item_counts,
            college=college,
            user_rankingpoint=user_ranking_point)


    ################

if __name__ == "__main__":
    application.run(host='0.0.0.0', debug = True)