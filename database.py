import pyrebase
import json 
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
        for res in users.each():
            value = res.val()
            if value['id'] == id_ and value['pw'] == pw_:
                return True
        return False
    
    #구매하기
    #가격 가져오기
    def get_price(self, name):
        point=int(self.db.child("item").child(name).get().val()['price'])
        return point
    #판매자 가져오기
    def get_seller(self, name):
        seller=self.db.child("item").child(name).get().val()['writer']
        return seller
    
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
        if user_data is not None and 'point' in user_data:
            b_point = int(user_data['rankingpoint'])
            a_point = b_point + point
            point_info = {
                "rankingpoint": a_point
            }
            self.db.child("user").child(user_id).update(point_info)
        return True


    ## 이 밑으로 쭉 다 내꺼
    
    #데이터베이스에 저장
    def reg_review(self, data, user_id, img_path):
        find_name = data['seller_id']+"_"+data['name'] #find_name=판매자id_상품명
        dbname = self.db.child("user").child(user_id).get() #db에 저장되어 있는 판매자id_상품명 찾기.
        college = dbname.val().get("college") #리뷰작성하는 유저의 대학 가지고옴 
        major = dbname.val().get("major")
        review_info ={
            "name": find_name, #판매자id_상품명
            "title": data['title'],
            "review": data['review'],
            "rate": data['reviewStar'],
            "keyword": data['keyword'],
            "img_path": img_path,
            "reviewer": user_id,
            "reviewer_college": college,
            "reviewer_major": major
        }
        name_id = find_name + '_' + user_id #판매자id_상품명_구매자id
        self.db.child("review").child(name_id).set(review_info)
        return True


    #상품별 리뷰 불러오기(상품별 리뷰화면)
    def get_reviews(self, target_name):
        all_review = self.db.child("review").get().val() #전체리뷰
        target_reviews = {}

        for review in all_review.each():                #각 리뷰에 대해 반복
            name = review.child("name").get().val()       #각 리뷰에 name value 추출
            if name == target_name:
                target_reviews[review.key()] = review.val()

        return target_reviews
    
    #상품별 리뷰 카테고리별로 불러오기(대학별 정렬)
    def get_reviews_bycategory(self,target_name, cate):
        all_review = self.db.child("review").get().val() #전체리뷰
        target_reviews = {}

        for review in all_review.each():                  #각 리뷰에 대해 반복
            name = review.child("name").get().val()       #각 리뷰에 name value 추출
            if name == target_name:
                target_reviews[review.key()] = review.val() #target_reviews = 특정 상품에 대한 리뷰들
                
        reviews = target_reviews.get()
        target_value=[]
        target_key=[]
        for res in reviews.each():
            value = res.val()
            key_value = res.key()
            
            if value['reviewer_college'] == cate:
                target_value.append(value)
                target_key.append(key_value)
        print("######target_value",target_value)
        new_dict={}
        
        for k,v in zip(target_key,target_value):
            new_dict[k]=v
            
        return new_dict
    
    
    #전체리뷰불러오기
    def get_all_reviews(self):
        all_reviews = self.db.child("review").get().val() 
        return all_reviews

    #이름으로 리뷰 불러오기(상세리뷰화면)
    def get_review_byname(self, name):                #name=판매자id_상품명
        reviews = self.db.child("review").get()
        target_value=""
        print("###########",name)
        for res in reviews.each():                 #각 리뷰마다 반복
            value = res.child("name").get().val()  #value = 리뷰내의 "name"(=판매자id_상품명)
            if value == name:                      #value = name 일때
                target_value=res.val()             #그 리뷰반환
        return target_value


    #구매내역 불러오기
    def get_purchase(self, user_id):
        purchase = self.db.child("user_purchase").get().val() #각 유저의 구매내역

        for id, purchase_items in purchase.items(): #각 리뷰에 대해 반복
            if id == user_id:                       #key값이 사용자 id와 같으면 그 구매내역 반환
                return purchase_items
        return None                                 #구매내역이 없는 경우


