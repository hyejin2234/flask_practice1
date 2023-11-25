import pyrebase
import json 

class DBhandler:
    def __init__(self ):
        with open('./authentication/firebase_auth.json') as f:
            config=json.load(f)

        firebase = pyrebase.initialize_app(config)
        self.db = firebase.database()
        
        
    # 회원가입
    def insert_user(self,data,pw,pw2):
        user_info={
            "id": data['id'],
            "pw":pw,
            "pw2":pw2,
            "email":data['email'],
            "hp":data['HP'],
            "college":data['dropdown1'],
            "major":data['dropdown2'],
            "nickname":data['nickname'],
            "point":30000,
            "rankingpoint":0
        }
        if self.id_duplicate_check(str(data['id'])) and self.nickname_duplicate_check(str(data['nickname'])):
            self.db.child("user").child(data['id']).set(user_info)
            print(data)
            return True
        else:
            return False
        
    # 회원가입 시 아이디 중복확인
    def id_duplicate_check(self, id_string):
        users = self.db.child("user").get()
        
        print("users###",users.val())
        if str(users.val()) == "None": # first registration
            return True
        else:
            for res in users.each():
                value = res.val()
                if value['id'] == id_string:
                    return False
            return True
    # 회원가입 시 닉네임 중복확인
    def nickname_duplicate_check(self, name_string):
        users = self.db.child("user").get()
        for res in users.each():
            value = res.val()
            if value['nickname'] == name_string:
                return False
        return True

    #유저 찾기
    def find_user(self, id_, pw_):
        users = self.db.child("user").get()
        target_value=[]
        for res in users.each():
            value = res.val()
            if value['id'] == id_ and value['pw'] == pw_:
                return True
        return False
    
    #구매자 포인트 감소
    def update_point(self, user_id, point):
        user_data = self.db.child("user").child(user_id).get().val()
        if user_data is not None and 'point' in user_data:
            b_point = int(user_data['point'])
            a_point = b_point - point
            point_info = {
                "point": a_point
            }
            self.db.child("user").child(user_id).update(point_info)
        return True
    #구매자 랭킹 포인트 증가
    def update_ranking_point(self, user_id, point):
        user_data = self.db.child("user").child(user_id).get().val()
        if user_data is not None and 'point' in user_data:
            b_point = int(user_data['rankingpoint'])
            a_point = b_point + point
            point_info = {
                "rankingpoint": a_point
            }
            self.db.child("user").child(user_id).update(point_info)
        return True




    ## 이 밑으로 쭉 다 내꺼
    #(커밋)상품명까지 데이터베이스에 담음
    def reg_review(self, data, img_path):
        review_info ={
            "name": data['name'],
            "title": data['title'],
            #"review": data['review'],
            "rate": data['reviewStar'],
            #"keyword": data['keyword'],
            "img_path": img_path,
            #"reviewer": session['id']
        }
        self.db.child("review").child(data['name']).child(data['title']).set(review_info)
        return True


    #커밋
    def get_reviews(self, target_name):
        all_review = self.db.child("review").get()
        
        for review in all_review.each():
            name = review.key()
            review = review.val()
            if name == target_name:
                target_reviews[name] = review
        reviews = self.db.child("review").order_by_child(session['id']).equal_to(target_name).get().val()
        return reviews

    #커밋 전체리뷰불러오기
    def get_all_reviews(self):
        reviews = self.db.child("review").get().val() #vla로 보내도 되는 지 모르겠음
        return reviews

