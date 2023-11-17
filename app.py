from flask import Flask, render_template, request 
import sys
application = Flask(__name__)
 
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
@application.route("/5~7/5")
def view_reg_review():
    return render_template("5~7/5.html")

@application.route("/5~7/6")
def view_reviews():
    return render_template("5~7/6.html")

@application.route("/5~7/7")
def view_review_detail():
    return render_template("5~7/7.html")


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