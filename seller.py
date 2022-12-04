from flask import Flask, Response, request,flash, render_template, make_response, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import json
from datetime import datetime


app=Flask(__name__)
CORS(app)

app.config['SECRET_KEY']='zy112612' # 密码
app.config['SQLALCHEMY_DATABASE_URI']='mysql+pymysql://admin:zy112612@e6156-1.cudpmdtzmg9e.us-east-1.rds.amazonaws.com:3306/Seller'
    # 协议：mysql+pymysql
    # 用户名：root
    # 密码：2333
    # IP地址：localhost
    # 端口：3306
    # 数据库名：runoob #这里的数据库需要提前建好
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN']=True
db=SQLAlchemy(app)

#测试连上
with app.app_context():
    sql = 'select * from Sellers'
    result = db.session.execute(sql)
    print(result.fetchall())


@app.route('/', methods=['GET'])
def home():
    return 'Hello World!'


#{"username":"ywang", "password":"0002", "email": "wg@gmail.com", "address": "400w"}
@app.route('/seller/register', methods=['GET', 'POST'])
def register():
    response = ""
    if request.method == 'POST':
        data = json.loads(request.get_data())

        username = data['username']
        password = data['password']
        email = data['email']
        address = data['address']
        print(email)
        try:
            sql = "SELECT COUNT('{}') FROM Sellers where email = '{}' ".format(email, email)
            result = db.session.execute(sql).fetchall()[0][0]
        except Exception as err:
            return {"state": False, "message": "error! input error"}
        
        print(result)
        if result > 0:
            response = {"state": False,"message": "error! email is used"}
        else:
            try:
                sql= "INSERT INTO Sellers VALUES ('{}', '{}', '{}', '{}');".format(email,username, password, address)
                db.session.execute(sql)
            except Exception as err:
                return {"state": False,"message": "error! input error"}
            sql = 'select * from Sellers'
            result = db.session.execute(sql)
            print(result.fetchall())
            
            response = {"state": True,"message": "register successfully"}
       
    return response

#{ "password":"0002", "email": "wg@gmail.com"}
@app.route('/seller/login', methods=['GET', 'POST'])
def login():
    
    if request.method == 'POST':
        data = json.loads(request.get_data())
        password = data['password']
        email = data['email']
        
        try:
            sql = "SELECT * FROM Sellers where email = '{}' ".format(email)
            result = db.session.execute(sql).fetchone()
        except Exception as err:
            return {"state": False, "message": "error! input error"}
        
        if result :
            stored_username= result[1]
            stored_password= result[2]
            stored_address= result[3]
            print(stored_username)
            if stored_password == password:
                print("successfully")
                response= {"state": True, "message":"login successfully", "username": stored_username, "address": stored_address}
            else:
                print("unmatch")
                response= {"state": False,"message":"password unmatch"}
        else:
            print("please register")
            response= {"state": False, "message": "you need to register firstly"}
        
    return response

#{ "currPw":"0002", "email": "wg@gmail.com", "modifiedPw": "0003"}
@app.route('/seller/modifyPassword', methods=['GET', 'POST'])
def customer_modify_password():
    if request.method == 'POST':
        data = json.loads(request.get_data())
        email = data['email']
        oldpwd = data['currPw']
        newpwd = data['modifiedPw']
        print(data)

        try:
            sql = "SELECT * FROM Sellers where Email = '{}' AND Pwd = '{}'".format(email, oldpwd)
            result = db.session.execute(sql).fetchone()
        except Exception as err:
            return {"message": "error! change password error","state":False}

        if result :
            stored_password= result[2]
            print(stored_password)
            try: 
                sql = "UPDATE Sellers SET Pwd = '{}' where Email = '{}'".format(newpwd, email)
                db.session.execute(sql)
            except Exception as err:
                return {"message": "error! change password error","state":False}
            try:
                sql = 'select * from Sellers'
                result = db.session.execute(sql)
                print(result.fetchall())
            except Exception as err:
                return {"message": "error! change password error","state":False}
            msg = {"message":"password modified successfully","state":True}
        else:
            msg = {"message":"old password unmatch","state":False}

        return msg

#{"address":"aaaa", "email": "wang@gmail.com", "username":"yifan"}
@app.route('/seller/modifyInfo', methods=['GET', 'POST'])
def customer_modify_information():
    if request.method == 'POST':
        data = json.loads(request.get_data())
        email = data['email']
        username = data['username']
        address = data['address']

        
        try: 
            sql = "UPDATE Sellers SET Name = '{}', address = '{}'  where Email = '{}'".format(username, address, email)
            db.session.execute(sql)
        except Exception as err:
            return {"message": "error! change information error","state":False}
        
        try:
            sql = 'select * from Sellers'
            result = db.session.execute(sql)
            print(result.fetchall())
        except Exception as err:
            return {"message": "error! change information error","state":False}
        
        msg = {"message":"information modified successfully","state":True}

        return msg

@app.route("/customer/search", methods=['GET', 'POST'])
def search():
    rsp=""
    if request.method == 'POST':
        data = json.loads(request.get_data())
       
        item = data['search_details']
        low_price = float(data['filter_conditions']['lowest_price'])
        high_price = float(data['filter_conditions']['highest_price'])
        sort= data['filter_conditions']['order']
        print(type(low_price))
        json_list=[]
        
        if sort =="decreasing_order":
          print("in")
          try:
            sql = "SELECT m.MID, m.Name, m.Price, m.RemainingAmount, m.Description, m.Picture1, m.Picture2, m.Picture3 FROM Merchandises m WHERE m.Description LIKE '%{}%' AND m.Price >= {} AND m.Price <= {} ORDER BY m.Price DESC".format(item, low_price, high_price)
            result = db.session.execute(sql).fetchall()
            print("incre")
          except Exception as err:
            return {"message": "input is wrong","state":False}
         
        else:
          try:
            sql = "SELECT m.MID, m.Name, m.Price, m.RemainingAmount, m.Description, m.Picture1, m.Picture2, m.Picture3 FROM Merchandises m WHERE m.Description LIKE '%{}%' AND m.Price >= {} AND m.Price <= {} ORDER BY m.Price ASC".format(item, low_price, high_price)
            result = db.session.execute(sql).fetchall()
          except Exception as err:
            return {"message": "input is wrong","state":False}

        for row in result:
            json_list.append([x for x in row])       

    return json_list


@app.route("/seller/show_item", methods=['GET', 'POST'])
def show_item():
    if request.method == 'POST':
        data = json.loads(request.get_data())
        email = data['email']
        try:
            sql = "SELECT m.MID, m.Name, m.Price, m.RemainingAmount, m.Description, m.Picture1 FROM Provides p, Merchandises m WHERE p.email = '{}' and p.MID = m.MID".format(email)
            result = db.session.execute(sql).fetchall()
        except Exception as err:
            return {"message": "input is wrong"}
        json_list=[]
        for row in result:
            json_list.append([x for x in row])       

    return json_list



@app.route("/seller/insert_item", methods=['GET', 'POST'])
def insert_item():
    response = ""
    if request.method == 'POST':
        data = json.loads(request.get_data())

        email = data['email']
        name = data['name']
        price = data['price']
        remaining_amount = data['remaining_amount']
        description = data['description']
        picture = data['picture']

        #compute the next mid
        try:
            sql= "SELECT max(mid) FROM Merchandises"
            result = db.session.execute(sql).fetchone()[0]
        except Exception as err:
            return {"state": False,"message": "error! input error"}
        prev_id = result
        curr_id = prev_id+1

        try:
            sql= 'INSERT INTO Merchandises VALUES ("{}","{}","{}","{}","{}","{}","{}","{}");'.format(curr_id, name, price, remaining_amount, description, picture,None,None)
            db.session.execute(sql)
        except Exception as err:
            return {"state": False,"message": "error! input error"}

        try:
            sql= "INSERT INTO Provides VALUES ('{}', '{}');".format(email, curr_id)
            db.session.execute(sql)
        except Exception as err:
            return {"state": False,"message": "error! input error"}

        #######for test#######
        sql = 'select * from Merchandises'
        result = db.session.execute(sql)
        print(result.fetchall())
        #######################
            
        response = {"state": True,"message": "insert item successfully"}
       
    return response

@app.route("/seller/update_item", methods=['GET', 'POST'])
def update_item():
    response = ""
    if request.method == 'POST':
        data = json.loads(request.get_data())

        email = data['email']
        mid = data['mid']
        name = data['name']
        price = data['price']
        remaining_amount = data['remaining_amount']
        description = data['description']
        picture = data['picture']

        #check if email own mid
        try:
            sql = "SELECT * FROM Provides WHERE Email = '{}' and MID = '{}';".format(email, mid)
            result = db.session.execute(sql).fetchall()[0]
        except Exception as err:
            print(err)
            return {"state": False,"message": "error! input error"}
        if len(result) > 0:
            # try:
                # sql= "UPDATE Merchandises SET Name = '{}', Price = '{}', RemainingAmount = '{}', Description = '{}', Picture1 = '{}' WHERE mid = '{}';".format(name, price, remaining_amount, description, picture, mid)
                # db.session.execute(sql)

                # db.session.execute('UPDATE Merchandises SET Name = (%s), Price = (%s), RemainingAmount = (%s), Description = (%s), Picture1 = (%s) WHERE mid = (%s)', name, price, remaining_amount, description, picture, mid)

            try:
                sql= "DELETE FROM Provides WHERE mid = '{}';".format(mid)
                db.session.execute(sql)
            except Exception as err:
                return {"state": False,"message": "error! delete Provides error"}

            try:
                sql= "DELETE FROM Merchandises WHERE mid = '{}';".format(mid)
                db.session.execute(sql)
            except Exception as err:
                return {"state": False,"message": "error! delete Merchandises error"}

            try:
                sql= "INSERT INTO Merchandises VALUES ('{}', '{}', '{}', '{}', '{}', '{}','{}','{}');".format(mid, name, price, remaining_amount, description, picture,None,None)
                db.session.execute(sql)
            except Exception as err:
                return {"state": False,"message": "error! insert Merchandises error"}

            try:
                sql= "INSERT INTO Provides VALUES ('{}', '{}');".format(email, mid)
                db.session.execute(sql)
            except Exception as err:
                return {"state": False,"message": "error! insert provides error"}

            # except Exception as err:
            #    return {"state": False,"message": "error! input error"}
        else:
            response = {"state": False,"message": "error! this is not your item"}
            

        #######for test#######
        sql = 'select * from Merchandises'
        result = db.session.execute(sql)
        print(result.fetchall())
        #######################
            
        response = {"state": True,"message": "update item successfully"}
       
    return response

@app.route("/seller/delete_item", methods=['GET', 'POST'])
def delete_item():
    response = ""
    if request.method == 'POST':
        data = json.loads(request.get_data())

        email = data['email']
        mid = data['mid']

        ######TODO: check if email own mid
        try:
            sql = "SELECT * FROM Provides WHERE Email = '{}' and MID = '{}';".format(email, mid)
            result = db.session.execute(sql).fetchall()[0][0]
        except Exception as err:
            print(err,1)
            return {"state": False,"message": "error! input error"}
        if len(result) > 0:
            try:
                sql= "DELETE FROM Provides WHERE mid = '{}';".format(mid)
                db.session.execute(sql)
            except Exception as err:
                print(err,2)
                return {"state": False,"message": "error! input error"}

            try:
                sql= "DELETE FROM Merchandises WHERE mid = '{}';".format(mid)
                db.session.execute(sql)
            except Exception as err:
                print(err,3)
                return {"state": False,"message": "error! input error"}
        else:
            response = {"state": False,"message": "error! this is not your item"}


        #######for test#######
        sql = 'select * from Merchandises'
        result = db.session.execute(sql)
        print(result.fetchall())
        #######################
            
        response = {"state": True,"message": "delete item successfully"}
       
    return response

@app.route("/people/<email>", methods=["GET"])
def get_customer_by_email(email):
    
    sql = "select * from Sellers where email = '" + email + "'"
    result = db.session.execute(sql).fetchone()

    if result:
        data_email=result[0]
        name=result[1]
        password= result[2]
        address= result[3]
        list=[data_email, name, password, address]
        
        rsp = Response(json.dumps(list), status=200, content_type="application/json")
        
    else:
        rsp = Response("NOT FOUND", status=404, content_type="text/plain")

    return rsp
    


if __name__=='__main__':
    app.run(host='0.0.0.0', port=8081, debug=True)
