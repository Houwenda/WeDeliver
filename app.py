import sys, json, redis
from flask import *
from flask_session import Session
from dbaction import *

app = Flask(__name__)
rds = redis.StrictRedis.from_url('redis://@127.0.0.1:6379')
app.config['SESSION_COOKIE_NAME'] = 'WESESSID'
app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_KEY_PREFIX'] = 'wedeliver:session:'
app.config['SESSION_REDIS'] = rds
Session(app)
app_id = 'wxca274128ca35c80b'
app_secret = '07d2173fc3989b8d23642519f8de0f4f'

@app.route('/api/deliver/data/', methods=['GET'])
def deliver_data():
    res = selectOrderByStatus(2)
    if not res:
        return json.dumps({'return_code': 301})
    return json.dumps(res)


@app.route('/api/deliver/publish/', methods=['POST'])
def deliver_publish():
    sess = session.get('WESESSID', None)
    if not sess:
        return json.dumps({'return_code': 101})
    userInfo = selectUserById(str(sess['openid']))
    if userInfo == None:
        return json.dumps({'return_code': 102})
    if not json.loads(request.values.get('time')):
        time = str(json.loads(request.values.get('time')))
    else:
        return json.dumps({'return_code': 302})
    if not json.loads(request.values.get('cargo')):
        cargo = str(json.loads(request.values.get('cargo')))
    else:
        return json.dumps({'return_code': 302})
    if not json.loads(request.values.get('ps')):
        ps = str(json.loads(request.values.get('ps')))
    else:
        return json.dumps({'return_code': 302})
    insertOrder(oid=genOID(), sts=3, rid='', did=sess['openid'], tm=time, cg=cargo, rw=0, ps=ps)
    return json.dumps({'return_code': 0})


@app.route('/api/deliver/match/', methods=['POST'])
def deliver_match():
    sess = session.get('WESESSID', None)
    if not sess:
        return json.dumps({'return_code': 101})
    rid = str(sess['openid'])
    userInfo = selectUserById(rid)
    if userInfo == None:
        return json.dumps({'return_code': 102})
    if not json.loads(request.values.get('time')):
        time = str(json.loads(request.values.get('time')))
    else:
        return json.dumps({'return_code': 302})
    if not json.loads(request.values.get('cargo')):
        cargo = str(json.loads(request.values.get('cargo')))
    else:
        return json.dumps({'return_code': 302})
    if not json.loads(request.values.get('reward')):
        reward = int(json.loads(request.values.get('reward')))
    else:
        return json.dumps({'return_code': 302})
    ps = str(json.loads(request.values.get('ps')))
    did = selectOrderById(request.values.get('deliverOrderId'))[2]
    oid = genOId()
    sts = 2
    insertOrder(oid, sts, did, rid, time, cargo, reward, ps)
    formerCargo = selectOrderById(did)[5]
    formerCargo['num'] -= cargo['num']
    updateOrdersCargoById(request.values.get('deliverOrderId'), json.dumps(formerCargo))
    if formerCargo['num'] == 0:
        updateOrdersStatusById(request.values.get('deliverOrderId'), 4)
    return json.dumps({'return_code': 0})


@app.route('/api/receiver/data/', methods=['GET'])
def receiver_data():
    res = selectOrderByStatus(3)
    if not res:
        return json.dumps({'return_code': 301})
    return json.dumps(res)


@app.route('/api/receiver/publish/', methods=['POST'])
def receiver_publish():
    sess = session.get('WESESSID', None)
    if not sess:
        return json.dumps({'return_code': 101})
    userInfo = selectUserById(str(sess['openid']))
    if userInfo == None:
        return json.dumps({'return_code': 102})
    if not json.loads(request.values.get('time')):
        time = str(json.loads(request.values.get('time')))
    else:
        return json.dumps({'return_code': 302})
    if not json.loads(request.values.get('cargo')):
        cargo = str(json.loads(request.values.get('cargo')))
    else:
        return json.dumps({'return_code': 302})
    if not json.loads(request.values.get('reward')):
        reward = int(json.loads(request.values.get('reward')))
    else:
        return json.dumps({'return_code': 302})
    if not json.loads(request.values.get('ps')):
        ps = str(json.loads(request.values.get('ps')))
    else:
        return json.dumps({'return_code': 302})
    if userInfo[2] - reward >= 0:
        insertOrder(genOID(), sts=2, rid=sess['openid'], did='', tm=time, cg=cargo, rw=reward, ps=ps)
        return json.dumps({'return_code': 0})
    return json.dumps({'return_code': 303})


@app.route('/api/receiver/match/', methods=['POST'])
def receiver_match():
    sess = session.get('WESESSID', None)
    did = str(sess['openid'])
    if not sess:
        return json.dumps({'return_code': 101})
    if userInfo == None:
        return json.dumps({'return_code': 102})
    updateOrdersDIDById(request.values.get('receiverOrderId'), did)
    updateOrdersStatusById(request.values.get('receiverOrderId'), 5)
    return json.dumps({'return_code': 0})


@app.route('/api/signing/', methods=['GET'])
def signing():
    sess = session.get('WESESSID', None)
    if not sess:
        return json.dumps({'return_code': 101})
    userInfo = selectUserById(str(sess['openid']))
    if userInfo == None:
        return json.dumps({'return_code': 102})
    OrderID = request.values.get('OrderId')
    ReceiverOrderData = selectOrderById(str(OrderID))
    ReceiverID = ReceiverOrderData[3]
    status = ReceiverOrderData[1]
    reward = ReceiverOrderData[6]
    DeliverID = ReceiverOrderData[2]
    DeliverData = selectUserById(DeliverID)
    if ReceiverID == str(sess['openid']):
        if status == 5:
            updateOrdersStatusById(OrderID, 0)
            points = DeliverData[2]
            updateUsersPointsById(DeliverID, points + reward)
            return json.dumps({'return_code': 0})
    else:
        return json.dumps({'return_code': 501})


from wx_login import Login

@app.route('/api/user/', methods=['GET'])
def user():
    sess = session.get('WESESSID', None)
    if not sess:
        return json.dumps({'return_code': 101})
    userInfo = selectUserById(sess['openid'])
    if userInfo == None:
        return json.dumps({'return_code': 102})
    return json.dumps({'return_code': 0, 'Raddr': userInfo[1], 'points': userInfo[2], 'userData': userInfo[3]})


@app.route('/api/user/login/', methods=['POST'])
def login():
    user_code = str(request.values.get('code'))
    enc = str(request.values.get('encryptedData'))
    iv = str(request.values.get('iv'))
    L = Login(user_code, enc, iv)
    if L.is_login():
        return json.dumps({'return_code': 0})
    return json.dumps({'return_code': L.errcode})


@app.route('/api/user/new/', methods=['POST'])
def newuser():
    sess = session.get('WESESSID', None)
    if not sess:
        return json.dumps({'return_code': 101})
    Raddr = request.values.get('Raddr')
    insertUser(sess['openid'], Raddr, 100, sess['userData'])
    return json.dumps({'return_code': 0})


import random

def genOID():
    while True:
        id = random.randint(10)
        res = selectOrderById(id)
        if res is None:
            break

    return id
