import pyrebase
import json 

class DBhandler:
    def __init__(self ):
        with open('./authentication/firebase_auth.json') as f:
            config=json.load(f)

        firebase = pyrebase.initialize_app(config)
        self.db = firebase.database()
   
    #커밋
    def reg_reveiw(self, data, img_path):
        review_info ={
            "title": data['reviewTitle'],
            "review": data['reviewContents'],
            "rate": data['reviewStar'],
            "keyword": data[''], # keyword 정보 받아와야되는데... 어떻게?
            "img_path": img_path,
            "reviewer": data[''] # 리뷰작성한 유저정보 가지고 와야 되는데..얘는 어떻게 데려와?
        }
        self.db.child("review").child(data['name']).child(data['reviewer']).set(review_info)  #데이터베이스에 저장
        return True


    #커밋
    def get_reviews(self, target_name): 
        reviews = self.db.child("review").order_by_child("name").equal_to(target_name).get().val()
        return reviews

    #커밋
    def get_all_reviews(self): 
        reviews = self.db.child("review").get().val() #vla로 보내도 되는 지 모르겠음
        return reviews

