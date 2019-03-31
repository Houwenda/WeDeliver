import sys
import json
import redis
from flask import *
from flask_session import Session
from wx_login import Login
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
rds = redis.StrictRedis.from_url(os.environ.get('REDIS_URL'))
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
@app.route('/api/deliver/data', methods=['GET'])
def deliver_data():
    res = selectOrderByStatus(2)
    if not res:
        return {'ret': -1}
    else:

        rr = {res['OrderID']:{res['RID'], res['Cargo'], res['Reward'], res['PS'] }}
        return json.dumps(rr)


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
        #  -1: not logined
        return {'ret' : -1}
    userInfo = selectUserById(str(sess['openid']))
    if (userInfo == (None,None,None)):
        # -2: not registered
        return {'ret' : -2}

    #time  string ,and format is "year.month.day.hour(24).minute.second"
    time = str(json.loads(request.values.get("time")))
    #cargo 
    cargo = str(json.loads(request.values.get("cargo")))
    #reward  int
    reward = int(json.loads(request.values.get("reward")))
    #ps string
    ps = int(json.loads(request.values.get("ps")))

    insertOrder(sts=3, rid='', did=sess['openid'], tm=time, cg=cargo, rw=reward, ps=ps)


# api for Receiver to match a deliver order 
@app.route('/api/deliver/match', methods=['POST'])
def deliver_match():
    pass


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
        return {'ret': -1}
    else:
        
        rr = {res['OrderID']:{res['DID'], res['Cargo'], res['Reward'], res['PS'] }}
        return json.dumps(rr)

#api for deliver to publish the order
#this api handle the request, and deposited the data into the database
@app.route('/api/receiver/publish', methods=['POST'])
def receiver_publish():
    sess = flask.session.get('WESESSID', None)
    if not sess:
        #  -1: not logined
        return {'ret' : -1}
    userInfo = selectUserById(str(sess['openid']))
    if (userInfo == (None,None,None)):
        # -2: not registered
        return {'ret' : -2}

    #time  string ,and format is "year.month.day.hour(24).minute.second"
    time = str(json.loads(request.values.get("time")))
    #cargo 
    cargo = str(json.loads(request.values.get("cargo")))
    #reward  int
    reward = int(json.loads(request.values.get("reward")))
    #ps string
    ps = int(json.loads(request.values.get("ps")))

    insertOrder(sts=2, rid=sess['openid'], did='', tm=time, cg=cargo, rw=reward, ps=ps)


@app.route('/api/receiver/match', methods=['POST'])
def receiver_match():
    pass

#===================================
# user api 
#===================================
@app.route('/api/user/')
def user():
    sess = flask.session.get('WESESSID', None)
    if not sess:
        #  -1: not logined
        return {'ret' : -1}
    userInfo = selectUserById(str(sess['openid']))
    if (userInfo == (None,None,None)):
        # -2: not registered
        return {'ret' : -2}
    return json.dumps('{'+ userInfo[1] +',' + userInfo[2] + '}')


#login api
@app.route('/api/user/login/', methods=['POST'])
def login():
    user_code = str(request.values.get("code"))
    L = Login(user_code)
    if L.is_login():
        return json.dumps({'ret': L.errcode})

@app.route('/api/user/new/', methods=['POST'])
def newuser():
    sess = flask.session.get('WESESSID', None)
    if  not sess:
        return {'ret' : -1}
    Raddr = request.values.get('Raddr')
    insertUser(str(sess['openid']), Raddr, 100)
    return {'ret' : 0}

if __name__ == '__main__':
    app.run(port=8000, debug=True)