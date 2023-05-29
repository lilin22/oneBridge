import base64
import json
import requests
from common.parseconf import parselgncf
from common.log import *
from models import baseDir

def loginServer():
    lgn_uri,username,password = parselgncf(baseDir)
    psw = base64.b64decode(password)
    password = bytes.decode(psw)
    headers = {'Content-Type': 'application/json;charset=utf-8'}
    params = {"username":username,"password":password}
    logger.info("登录easyTest平台的请求参数：" + json.dumps(params, ensure_ascii=False))
    response = requests.post(url=lgn_uri, headers=headers, data=json.dumps(params, ensure_ascii=False).encode("utf-8"))
    res = response.text
    res = json.loads(res)
    logger.info("登录easyTest平台的返回内容：" + json.dumps(res, ensure_ascii=False))
    return res['access']

if __name__ == '__main__':
    loginServer()