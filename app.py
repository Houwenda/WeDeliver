import sys
import json
import redis
from flask import *
from flask_session import Session
import wx_login
from  dbaction import *

#test
'''
defaultencoding = "utf-8"
if sys.getdefaultencoding() != defaultencoding:
    reload(sys)
    sys.setdefaultencoding(defaultencoding)
'''


#----------------------Initailization--------------
app = Flask(__name__)
rds = redis.StrictRedis.from_url("redis://@127.0.0.1:6379")
app.config['SESSION_COOKIE_NAME'] = 'WESESSID'
app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_KEY_PREFIX'] = 'wedeliver:session:'
app.config['SESSION_REDIS'] = rds
Session(app)
app_id = 'wxca274128ca35c80b'  ##
app_secret = '07d2173fc3989b8d23642519f8de0f4f'  ##

#----------------------Route-----------------------

# @TODO: coupling deliver and receiver api
# @Issue: Should we refactor the order list?
#       the problem is that a deliver order can only match only one receiver's order
#       As for auto-match, we have to
#

#===================================
# deliver api
#===================================

# api for deliver_data
# Return json
# ret   -1: no data

# @Issue  how to choose time column
# res['Time'] ??
# @Issue   how to paginate
# limit ? offset ?


# return_code {
#
#              0: success
# user{
#
#              101:not login
#              102:not registered
#              103:don't have  permission
#              104:server error, connot connect to wechat server or server is busy
#              105:invalid js_code
#
#       }
#database{
#              201:don't have this value
#              202:invalid  value
#              203:database connect error
# }
#publish{
#              301:publish failed
#              302:invalid data
#              303:insufficient balance
# }
#match{
#              401:connot find matchable order
# }
#signing{
#              501:wrong ReveiverID or OrderID
#               
# }
#
#
#
#
#
# }


@app.route('/api/deliver/data', methods=['GET'])
def deliver_data():
    res = selectOrderByStatus(2)
    if not res:
        return json.dumps({'return_code': 301})
    else:
         #rr = {res['OrderID']:{res['RID'], res['Cargo'], res['Reward'], res['PS'] }}
        return json.dumps(res)


#api for deliver to publish the order
#this api handle the request, and deposited the data into the database
@app.route('/api/deliver/publish', methods=['POST'])
def deliver_publish():
    #OrderID  string
    #OrderID = str(json.loads(request.values.get("OrderID")))
    #DID   string
    #DID = str(json.loads(request.values.get("DID")))
    sess = flask.session.get('WESESSID', None)
    if not sess:
        return json.dumps({'return_code' : 101})
    userInfo = selectUserById(str(sess['openid']))
    if (userInfo == None):
        return json.dumps({'return_code' : 102})

    if not json.loads(request.values.get("time")):
        #time  string ,and format is "year.month.day.hour(24).minute.second"
        time = str(json.loads(request.values.get("time")))
    else:
        return json.dumps({'return_code':302})


    if not json.loads(request.values.get("cargo")):
        #cargo
        cargo = str(json.loads(request.values.get("cargo")))
    else:
        return json.dumps({'return_code':302})


    if not json.loads(request.values.get("ps")):
        #ps string
        ps = str(json.loads(request.values.get("ps")))
    else:
        return json.dumps({'return_code':302})

    insertOrder(oid = genOID(),sts = 3, rid = '', did = sess['openid'], tm = time, cg = cargo, rw = 0, ps=ps)
    return json.dumps({'return_code': 0})



# api for Receiver to choose a deliver order
@app.route('/api/deliver/match', methods=['POST'])
def deliver_match():
    sess = flask.session.get('WESESSID', None)
    if not sess:
        return json.dumps({'return_code' : 101})
    rid = str(sess['openid'])
    userInfo = selectUserById(rid)
    if (userInfo == None)):

        return json.dumps({'return_code' : 102})

    if not json.loads(request.values.get("time")):
        #time  string ,and format is "year.month.day.hour(24).minute.second"
        time = str(json.loads(request.values.get("time")))
    else:
        return json.dumps({'return_code':302})


    if not json.loads(request.values.get("cargo")):
        #cargo
        cargo = str(json.loads(request.values.get("cargo")))
    else:
        return json.dumps({'return_code':302})


    if not json.loads(request.values.get("reward")):
        #reward  int
        reward = int(json.loads(request.values.get("reward")))
    else:
        return json.dumps({'return_code':302})

    ps = str(json.loads(request.values.get("ps")))
    did = selectOrderById(request.values.get("deliverOrderId"))[2]
    oid = genOId()
    sts = 2
    insertOrder(oid, sts, did, rid, time, cargo, reward, ps)
    formerCargo = selectOrderById(did)[5]
    formerCargo['num'] -= cargo['num']
    updateOrdersCargoById(request.values.get("deliverOrderId"), json.dumps(formerCargo))
    if (formerCargo['num'] == 0):
        updateOrdersStatusById(request.values.get("deliverOrderId"), 4)
    return json.dumps({'return_code': 0})

#===================================
# receiver api
#===================================

# api for receiver_data
# Return json
# @Issue same as deliver_data
@app.route('/api/receiver/data', methods=['GET'])
def receiver_data():
    res = selectOrderByStatus(3)
    if not res:
        return json.dumps({'return_code':301})
    return json.dumps(res)

#api for deliver to publish the order
#this api handle the request, and deposited the data into the database
@app.route('/api/receiver/publish', methods=['POST'])
def receiver_publish():
    sess = flask.session.get('WESESSID', None)
    if not sess:
        return json.dumps({'return_code': 101})
    userInfo = selectUserById(str(sess['openid']))
    if (userInfo == None):
        return json.dumps({'return_code':102})

    if not json.loads(request.values.get("time")):
        #time  string ,and format is "year.month.day.hour(24).minute.second"
        time = str(json.loads(request.values.get("time")))
    else:
        return json.dumps({'return_code':302})


    if not json.loads(request.values.get("cargo")):
        #cargo
        cargo = str(json.loads(request.values.get("cargo")))
    else:
        return json.dumps({'return_code':302})


    if not json.loads(request.values.get("reward")):
        #reward  int
        reward = int(json.loads(request.values.get("reward")))
    else:
        return json.dumps({'return_code':302})


    if not json.loads(request.values.get("ps")):
        #ps string
        ps = str(json.loads(request.values.get("ps")))
    else:
        return json.dumps({'return_code':302})

    if (userInfo[2] - reward) >= 0 :
        insertOrder(genOID(),sts=2, rid=sess['openid'], did='', tm=time, cg=cargo, rw=reward, ps=ps)
        return json.dumps({'return_code': 0})
    else:
        return json.dumps({'return_code':303})



# api for Deliver to choose a receiver order
@app.route('/api/receiver/match', methods=['POST'])
def receiver_match():
    sess = flask.session.get('WESESSID', None)
    did = str(sess['openid'])
    if not sess:
        return json.dumps({'return_code' : 101})
    if (userInfo == None):
        return json.dumps({'return_code' : 102})
    updateOrdersDIDById(request.values.get("receiverOrderId"),did)
    updateOrdersStatusById(request.values.get("receiverOrderId"), 5)
    return json.dumps({'return_code': 0})

    
#==================================
#signing api
#==================================
#this api request receiver's orderID
@app.route('/api/signing/',methods = ['GET'])
def signing():
    sess = flask.session.get('WESESSID', None)
    if not sess:
        return json.dumps({'return_code' : 101})
    userInfo = selectUserById(str(sess['openid']))
    if (userInfo == None):
        return json.dumps({'return_code' : 102})
    OrderID = request.values.get("OrderId")
    #The URL format shoudle be https://www.wehaveworld.cn/api/signing/?OrderID=
    ReceiverOrderData = selectOrderById(str(OrderID))
    ReceiverID = ReceiverOrderData[3]
    status = ReceiverOrderData[1]
    reward = ReceiverOrderData[6]
    DeliverID = ReceiverOrderData[2]
    DeliverData = selectUserById(DeliverID)
    if ReceiverID == str(sess['openid']):
        if status == 5:
            updateOrdersStatusById(OrderID , 0)
            points = DeliverData[2]
            updateUsersPointsById(DeliverID, points+reward)
            return json.dumps({'return_code': 0})
    else:
        return json.dumps({'return_code':501})



#===================================
# user api
#===================================
@app.route('/api/user/',methods = ['GET'])
def user():
    sess = flask.session.get('WESESSID', None)
    if not sess:
        return json.dumps({'return_code' : 101})
    userInfo = selectUserById(str(sess['openid']))
    if (userInfo == None):
        return json.dumps({'return_code' : 102})
    return json.dumps('{'+ userInfo[1] +',' + userInfo[2] + '}')

#              104:server error, connot connect to wechat server or server is busy
#              105:invalid js_code

#login api
@app.route('/api/user/login/', methods=['POST'])
def login():
    user_code = str(request.values.get("code"))
    L = Login(user_code)
    if L.is_login():
        if L.errcode == -1 or L.errcode == 40029:
            return json.dumps({'return_code': 104})
        if L.errcode ==  40029:
            return json.dumps({'return_code': 105})
        else:
            return json.dumps({'return_code':0})

@app.route('/api/user/new/', methods=['POST'])
def newuser():
    sess = flask.session.get('WESESSID', None)
    if  not sess:
        return json.dumps({'return_code' : 101})
    Raddr = request.values.get('Raddr')
    insertUser(str(sess['openid']), Raddr, 100)
    return json.dumps({'return_code' : 0})

if __name__ == '__main__':
    app.run(port=8000, debug=True)
