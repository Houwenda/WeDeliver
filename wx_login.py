import requests
import json

app_id = ''  ##
app_secret = ''  ##

class login:
    js_code = ''
    openid = ''
    __session_key = ''
    errcode = -1
    errmsg = ''
    

    '''
    errcode values
    -1 	    系统繁忙，此时请开发者稍候再试
    0 	    请求成功
    40029 	code 无效
    45011 	频率限制，每个用户每分钟100次
    '''
    
    def __init__(self,code):
        self.js_code = code
        api = 'https://api.weixin.qq.com/sns/jscode2session'
        params = 'appid={0}&secret={1}&js_code={2}&grant_type=authorization_code' \
                .format(app_id,app_secret,self.js_code)
        url = api + '?' + params
        response = requests.get(url=url)
        result = json.loads(response.text)
        if 'errcode' in result and result['errcode']== 0:
            self.openid = result['openid']
            self.__session_key = result['session_key']
            self.errcode = result['errcode']
            self.errmsg = result['ermsg']
        else:
            pass


    
    def is_login(self):
        if self.errcode == 0:
            return True
        else:
            return False
    
    def back(self):
        res = {'openid': self.openid}
        return res
    
    def get_session_key(self):
        return self._login__session_key


