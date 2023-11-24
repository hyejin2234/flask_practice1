import pyrebase
import json 

class DBhandler:
    def __init__(self ):
        with open('./authentication/firebase_auth.json') as f:
            config=json.load(f)

        firebase = pyrebase.initialize_app(config)
        self.db = firebase.database()

    def reg_reveiw(self, data, img_path): #커밋
        review_info ={
            "title": data['reviewTitle'],
            "review": data['reviewContents'],
            "rate": data['reviewStar'],
           ## "keyword": data[''], # keyword 정보 받아와야되는데... 어떻게?
            "img_path": img_path,
           ## "reviewer": data[''] # 리뷰작성한 유저정보 가지고 와야 되는데..얘는 어떻게 데려와?
        }
        self.db.child("review").child(data['name']).child('reviewer').set(review_info)  #데이터베이스에 저장
        return True
    
    def get_reviews(self, target_name):  #커밋
        reviews = self.db.child("review").order_by_child("name").equal_to(target_name).get().val()
        return reviews

