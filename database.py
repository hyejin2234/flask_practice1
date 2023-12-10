import pyrebase
import json 
import time
from datetime import datetime

class DBhandler:
    def __init__(self ):
        with open('./authentication/firebase_auth.json') as f:
            config=json.load(f )

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
        if self.id_duplicate_check(str(data['id'])) and self.nickname_duplicate_check(str(data['nickname'])and (pw==pw2)):
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
        if users is None or users.val() is None:
            return True

        for res in users.each():
            value = res.val()
            if value['nickname'] == name_string:
                return False
        return True

    #유저 찾기
    def find_user(self, id_, pw_):
        users = self.db.child("user").get()
        for res in users.each():
            value = res.val()
            if value['id'] == id_ and value['pw'] == pw_:
                return True
        return False
    
    #구매하기
    #가격 가져오기
    def get_price(self, item_name):

        data = self.db.child("item").child(item_name).get().val()
        point=int(self.db.child("item").child(item_name).get().val()['price'])
        return point
    #판매자 가져오기
    def get_seller(self, name):
        seller=self.db.child("item").child(name).get().val()['writer']
        return seller
    
    #판매자 이메일 가져오기
    def get_seller_email(self, item_name):
        # "item" child에서 "name"에 해당하는 데이터의 "writer" 값을 가져오기
        writer = self.db.child("item").child(item_name).get().val().get('writer')
        if writer:
            # "user" child에서 "id"가 "writer"와 일치하는 데이터 찾기
            user_data = self.db.child("user").child(writer).get().val()
            if user_data:
                # 찾은 사용자의 정보에서 "email" 값을 반환
                email = user_data.get('email')
                return email
        # 찾지 못한 경우 None 반환
        return None

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
    #판매자 포인트 증가
    def update_point_2(self, user_id, point):
        user_data = self.db.child("user").child(user_id).get().val()
        if user_data is not None and 'point' in user_data:
            b_point = int(user_data['point'])
            a_point = b_point + point
            point_info = {
                "point": a_point
            }
            self.db.child("user").child(user_id).update(point_info)
        return True
    #구매자 판매자 랭킹 포인트 증가
    def update_ranking_point(self, user_id, point):
        user_data = self.db.child("user").child(user_id).get().val()
        if user_data is not None and 'rankingpoint' in user_data:
            b_point = int(user_data['rankingpoint'])
            a_point = b_point + point
            point_info = {
                "rankingpoint": a_point
            }
            self.db.child("user").child(user_id).update(point_info)
        return True
    
    #리뷰
    #리뷰 데이터베이스에 저장
    def reg_review(self, data, user_id, img_path):
        find_name = data['seller_id']+"_"+data['name'] #find_name=판매자id_상품명
        dbname = self.db.child("user").child(user_id).get() #db에 저장되어 있는 판매자id_상품명 찾기.
        college = dbname.val().get("college") #리뷰작성하는 유저의 대학 가지고옴 
        major = dbname.val().get("major")
        timestamp = int(time.time())
        review_info ={
            "name": find_name, #판매자id_상품명
            "title": data['title'],
            "review": data['review'],
            "rate": data['reviewStar'],
            "keyword": data['keyword'],
            "img_path": img_path,
            "reviewer": user_id,
            "reviewer_college": college,
            "reviewer_major": major,
            "timestamp": timestamp
        }
        name_id = find_name + '_' + user_id #판매자id_상품명_구매자id
        self.db.child("review").child(name_id).set(review_info)
        return True
    
    #상품별 리뷰 불러오기
    def get_reviews(self, target_name):
        all_review = self.db.child("review").get().val()
        target_reviews = {}
        
        for review_key, review_value in all_review.items():
            name  = review_value.get("name")
            if name == target_name:
                target_reviews[review_key] = review_value
    
        return target_reviews
    

    #상품별 리뷰 카테고리별로 불러오기(대학별 정렬)
    def get_reviews_bycategory(self,target_name, cate):
        all_review = self.db.child("review").get().val() #전체리뷰
        target_reviews = {}

        for review_key, review_value in all_review.items():
            name  = review_value.get("name")
            if name == target_name:
                target_reviews[review_key] = review_value  #target_reviews = 특정 상품에 대한 리뷰들

        reviews = list(target_reviews.values())  # 딕셔너리의 값들을 리스트로 변환

        target_value = []
        target_key = []

        for res in reviews:
            value = res
            key_value = review_key  # 루프에서 얻은 review_key를 사용
            if value.get('reviewer_college') == cate:
                target_value.append(value)
                target_key.append(key_value)
        print("######target_value",target_value)
        new_dict={}
        
        for k,v in zip(target_key,target_value):
            new_dict[k]=v
            
        return new_dict
    

    #전체리뷰불러오기
    # def get_all_reviews(self):
    #     reviews = self.db.child("review").get().val()
    #     return reviews
    
    #이름으로 리뷰불러오기(상세리뷰화면)
    def get_review_byname(self, name):
        reviews = self.db.child("review").get()
        target_value=""
        print("###########",name)
        for res in reviews.each():
            value = res.child("name").get().val()
            if value == name:
                target_value=res.val()
        return target_value
    
    
    #사용자별 구매내역 저장하기
    def insert_purchase_history(self, item_name, user_id):

        timestamp = int(time.time())

        purchase_info = {
            "item_name": item_name,
            "timestamp": timestamp
        }
        self.db.child("user_purchase_history").child(user_id).child(item_name).set(purchase_info)
        return True
    
    #사용자별 구매내역 가져오기
    def get_purchase_history(self, user_id):
        return self.db.child("user_purchase_history").child(user_id).get().val()

    #상품 정보 등록하기
    def insert_item(self, item_name, data, item_path, photo_path, user_id):

        timestamp = int(time.time())
        datetime_obj = datetime.utcfromtimestamp(timestamp)
        formatted_date = datetime_obj.strftime('%Y년 %m월 %d일 %H시 %M분 %S초')
        key_name = user_id + '_' + item_name

        item_info = {
            "writer": user_id,
            "item_name": data['item_name'],
            "item_type": data['item_type'],
            "price": data['price'],
            "course_type": data.get('course_type'),
            "faculty": data.get('faculty'),
            "major": data['major'],
            "course_name": data['course_name'],
            "course_number": data['course_number'],
            "professor": data['professor'],
            "description": data['description'],
            "tag": data['tag'],
            "item_path": item_path,
            "photo_path": photo_path,
            "download_count": 0,
            "timestamp": formatted_date,
            "average_star": 0,
            "review_count": 0,
            "key_name": key_name
        }
        user_and_item = user_id + '_' + data['item_name']
        self.db.child("item").child(user_and_item).set(item_info)
        print(data, item_path)
        for path in photo_path:
            print("사진 경로:", path)
        return True
    
    #상품 정보 불러오기
    def get_items(self):
        items = self.db.child("item").get().val()
        return items
    
    #상품 이름으로 상품 정보 가져오기
    def get_item_byname(self, name):
        items = self.db.child("item").get()
        target_value={}
        print("#############", name)
        for res in items.each():
            key_value = res.key()
            if key_value == name:
                target_value=res.val()
        return target_value
    
    #강의 이름으로 상품 정보 가져오기
    def get_item_by_coursename(self, course_name):
        items = self.db.child("item").get()
        target_value=[]
        target_key=[]
        for res in items.each():
            value=res.val()
            key_value = res.key()
            if value['course_name'] == course_name:
                target_value.append(value)
                target_key.append(key_value)
        
        print("######target_value", target_value)
        new_dict={}

        for k,v in zip(target_key, target_value):
                new_dict[k]=v

        return new_dict


    #heart 정보 가져오기
    def get_heart_byname(self, uid, name):
        hearts = self.db.child("heart").child(uid).get()
        target_value=""
        if hearts.val() == None:
            return target_value
        
        for res in hearts.each():
            key_value = res.key()
        
            if key_value == name:
                target_value=res.val()
        return target_value
        
    #heart 값 변경하기    
    def update_heart(self, user_id, isHeart, item):
        heart_info ={
            "interested": isHeart
        }
        self.db.child("heart").child(user_id).child(item).set(heart_info)
        return True

    #구매 버튼 누를 때마다 download 횟수 하나씩 늘려 저장
    def increase_download_count(self, item_name):
        # 현재 download_count 값을 가져옴
        current_count = self.db.child("item").child(item_name).child("download_count").get().val()

        # 현재 download_count 값을 1 증가시켜 업데이트
        new_count = current_count + 1
        self.db.child("item").child(item_name).update({"download_count": new_count})

        return new_count

    #현재 download 횟수 가져옴
    def get_download_count(self, item_name):
        # 현재 download_count 값을 가져와 반환
        return self.db.child("item").child(item_name).child("download_count").get().val()


    #리뷰 등록할 때마다 review 횟수 하나씩 늘려서 저장
    def increase_review_count(self, item_name):
        print(item_name)
        current_count = self.db.child("item").child(item_name).child("review_count").get().val()
        print(current_count)

        new_count = current_count + 1
        self.db.child("item").child(item_name).update({"review_count": new_count})
        
    #저장된 review 개수 불러오기
    def get_review_count(self, item_name):
        return self.db.child("item").child(item_name).child("review_count").get().val()


    #주어진 target_name(상품명)과 일치하는 리뷰의 별점 총합 계산하기
    def get_reviews_sum(self, target_name):
        reviews = self.db.child("review").get()
        total_rate = 0
        count = 0
        for review_data in reviews.each():
            review_data = review_data.val()  # `.each()`로 가져온 데이터는 `.val()` 메서드로 추출

            # 각 리뷰의 name이 목표하는 name과 일치하는지 확인
            if review_data.get("name") == target_name:
                total_rate += int(review_data.get("rate", 0))
                count += 1
        return total_rate
    
    #리뷰 등록될 때마다 average_star 값 업데이트하기
    def update_average_star(self, item_name, average_star):
        self.db.child("item").child(item_name).update({"average_star": average_star})

    #average_star 값 반환하기
    def get_average_star(self, item_name):
        return self.db.child("item").child(item_name).child("average_star").get().val()

    #사용자 포인트 가져오기
    def get_user_point(self, name):
        point=int(self.db.child("user").child(name).get().val()['point'])
        return point
    #사용자 랭킹포인트 가져오기
    def get_user_ranking_point(self, name):
        point=int(self.db.child("user").child(name).get().val()['rankingpoint'])
        return point
    #랭킹
    #유저 전체 가져오기
    def get_users(self ):
        items = self.db.child("user").get().val()
        return items
    #유저 대학 별 정렬
    def get_users_bycollege(self, cate):
        items = self.db.child("user").get()
        target_value=[]
        target_key=[]
        for res in items.each():
            value = res.val()
            key_value = res.key()
            if value['college'] == cate:
                target_value.append(value)
                target_key.append(key_value)
        print("######target_value",target_value)
        new_dict={}
        for k,v in zip(target_key,target_value):
            new_dict[k]=v
        return new_dict
    #아이템 전공 별 정렬
    def get_items_bymajor(self, cate):
        items = self.db.child("item").get()
        target_value=[]
        target_key=[]
        for res in items.each():
            value = res.val()
            key_value = res.key()
            if value['major'] == cate:
                target_value.append(value)
                target_key.append(key_value)
        print("######target_value",target_value)
        new_dict={}
        for k,v in zip(target_key,target_value):
            new_dict[k]=v
        return new_dict
    #아이템 타입 별 정렬
    def get_items_bycoursetype(self, coursetype):
        items = self.db.child("item").get()
        target_value=[]
        target_key=[]
        for res in items.each():
            value = res.val()
            key_value = res.key()
            if value['course_type'] == coursetype:
                target_value.append(value)
                target_key.append(key_value)
        print("######target_value",target_value)
        new_dict={}
        for k,v in zip(target_key,target_value):
            new_dict[k]=v
        return new_dict
    #아이템타입 별 정렬
    def get_items_byitemtype(self, coursetype):
        items = self.db.child("item").get()
        target_value=[]
        target_key=[]
        for res in items.each():
            value = res.val()
            key_value = res.key()
            if value['item_type'] == coursetype:
                target_value.append(value)
                target_key.append(key_value)
        print("######target_value",target_value)
        new_dict={}
        for k,v in zip(target_key,target_value):
            new_dict[k]=v
        return new_dict
    #수업타입/전공 별 정렬
    def get_items_bymajor_coursetype(self, major, course_type):
        items = self.db.child("item").get()
        target_value = []
        target_key = []
        for res in items.each():
            value = res.val()
            key_value = res.key()
            if value['major'] == major and value['course_type'] == course_type:
                target_value.append(value)
                target_key.append(key_value)
        new_dict = {}
        for k, v in zip(target_key, target_value):
            new_dict[k] = v
        return new_dict
    #아이템타입/전공 별 정렬
    def get_items_bymajor_item(self, major, item_type):
        items = self.db.child("item").get()
        target_value = []
        target_key = []
        for res in items.each():
            value = res.val()
            key_value = res.key()
            if value['major'] == major and value['item_type'] == item_type:
                target_value.append(value)
                target_key.append(key_value)
        new_dict = {}
        for k, v in zip(target_key, target_value):
            new_dict[k] = v
        return new_dict
    #아이템타입/수업타입 별 정렬
    def get_items_bycoursetype_itemtype(self, coursetype, item_type):
        items = self.db.child("item").get()
        target_value = []
        target_key = []
        for res in items.each():
            value = res.val()
            key_value = res.key()
            if value['course_type'] == coursetype and value['item_type'] == item_type:
                target_value.append(value)
                target_key.append(key_value)
        new_dict = {}
        for k, v in zip(target_key, target_value):
            new_dict[k] = v
        return new_dict
    
    #아이템타입/수업타입/전공 별 정렬
    def get_items_bymajor_coursetype_itemtype(self, major, coursetype, itemtype):
        items = self.db.child("item").get()
        target_value = []
        target_key = []
        for res in items.each():
            value = res.val()
            key_value = res.key()
            if value['course_type'] == coursetype and value['item_type'] == itemtype and value['major']==major:
                target_value.append(value)
                target_key.append(key_value)
        new_dict = {}
        for k, v in zip(target_key, target_value):
            new_dict[k] = v
        return new_dict
