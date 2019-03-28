import sys
from flask import *
import json
import wx_login

'''
defaultencoding = "utf-8"
if sys.getdefaultencoding() != defaultencoding:
    reload(sys)
    sys.setdefaultencoding(defaultencoding)
'''



app = Flask(__name__)


#api for deliver_data 
#this api return deliver data in json 
@app.route('/api/deliver_data',methods=['GET'])
def deliver_data():
    pass

#api for deliver to publish the order
#this api handle the request, and deposited the data into the database
@app.route('/api/deliver_publish',methods=['POST'])
def deliver_publish():
    #OrderID should be string
    OrderID = str(json.loads(request.values.get("OrderID")))
    #DID should be string
    DID = str(json.loads(request.values.get("DID")))
    #time should be string ,and format is "year.month.day.hour(24).minute.second"
    time = str(json.loads(request.values.get("time")))
    #
    cargo = str(json.loads(request.values.get("cargo")))
    #reward should be int
    reward = int(json.loads(request.values.get("reward")))



#api for receiver_data 
#this api return receiver data in json 
@app.route('/api/receiver_data',methods=['GET'])
def receiver_data():
    pass

#api for deliver to publish the order
#this api handle the request, and deposited the data into the database
@app.route('/api/receiver_publish',methods=['POST'])
def receiver_publish():
    pass

@app.route('/api/login',methods=['POST'])
def Login():
    user_code = str(request.values.get("code"))
    L = wx_login.login(user_code)
    res = L.back()
    if L.is_login():
        return json.dumps(res)




    


if __name__ == '__main__':
    app.run(debug=True)