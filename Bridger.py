from flask_restful import Resource, Api
from flask_docs import ApiDoc
from models import app, dbhandle, baseDir, userlogin, appManage, onLineDete, \
    startTestTask,casesBranch, caseRunningStatic
import json,pymysql,os,math,sys
from common.log import *
from flask import request, render_template, send_from_directory
from flask_cors import CORS
from common.login import loginServer
from common.parseconf import parsergtcf, parseahcf, parsedvscf, parsegtcrlcf, parseutttcf,parsedcecf,parsepjt,parseAppcf
from codes import code_success, msg_success,code_mde, msg_fail,code_fail,code_tokenError,msg_tokenError
import hashlib,telnetlib
from models import host,username,password,dbname,dbport
from common.mslunit import sqlConnect,truncate,selectAll,insert,delete,sqlcls
import requests,json
import datetime,time

lastReport_dir = r'C:\projects\oneCtl\lastReport'
PRO_PATH = r'C:\projects\one'

# Local loading
# app.config['API_DOC_CDN'] = False

# Disable document pages
# app.config['API_DOC_ENABLE'] = False

# RESTful Api documents to be excluded
app.config['RESTFUL_API_DOC_EXCLUDE'] = []
restful_api = Api(app)
ApiDoc(app)
CORS(app, supports_credentials=True)

cachedir = parsedcecf(baseDir)
report_dir = parsepjt(baseDir)

@app.route('/brain/home', methods=['get'])
def home():
    return render_template("index.html")


class register(Resource):
    """用户注册"""

    def post(self):
        """
        @@@
        #### args

        > {"username": "admin", "password": "admin"}

        #### return
        > {"code": code_success, "msg": msg_success}
        @@@
        """
        data = json.loads(request.get_data())
        logger.info('请求注册参数：' + json.dumps(data, ensure_ascii=False))
        username = data['username']
        password = data['password']
        user, psw = parsergtcf(baseDir)
        if username == user and password == psw:
            lgn = userlogin.query.filter_by(username="admin").first()
            if lgn == None:
                data = userlogin(username=username, password=password)
                dbhandle.session.add(data)
                dbhandle.session.commit()
                res_data = {"code": code_success, "msg": msg_success}
                logger.info('注册返回内容：' + json.dumps(res_data, ensure_ascii=False))
                return res_data
            else:
                res_data = {"code": code_mde, "msg": "该用户已经被注册"}
                logger.info('注册返回内容：' + json.dumps(res_data, ensure_ascii=False))
                return res_data
        else:
            res_data = {"code": code_fail, "msg": "只允许注册admin用户"}
            logger.error('注册返回内容：' + json.dumps(res_data, ensure_ascii=False))
            return res_data


class login(Resource):
    """用户登录"""

    def post(self):
        """
        @@@
        #### args

        > {"username": "admin", "password": "admin"}

        #### return
        > {"code": code_success, "msg": msg_success, "token": "557273a7a755f0e066b07bf27aeeec32"}
        @@@
        """
        if "=" in str(request.get_data()):
            reqdata = {}
            rqtdata = request.get_data().decode('utf-8', 'ignore')
            if "&" in rqtdata:
                reqlist = rqtdata.split('&')
                for rql in reqlist:
                    reqdt = "".join(rql)
                    reqdtlist = reqdt.split('=')
                    reqdata["".join(reqdtlist[0])] = "".join(reqdtlist[-1])
            else:
                reqdtlist = rqtdata.split('=')
                reqdata["".join(reqdtlist[0])] = "".join(reqdtlist[-1])
            rqutdata = json.dumps(reqdata)
            data = json.loads(rqutdata)
        else:
            data = json.loads(request.get_data())
        logger.info('请求登录参数：' + json.dumps(data, ensure_ascii=False))
        username = data['username']
        password = data['password']
        lgn = userlogin.query.filter_by(username="admin").first()
        timeNowStamp = time.mktime(datetime.datetime.now().timetuple())
        today = datetime.datetime.now()
        # 计算偏移量
        offset = datetime.timedelta(days=3)
        # 获取想要的日期的时间
        re_date = (today + offset).strftime('%Y-%m-%d')
        # nowTime = datetime.datetime.now().strftime('%H:%M')
        app, version, srcret_key = parseahcf(baseDir)
        if (username == lgn.username and password == lgn.password):
            if lgn.token == None:
                dt = str(timeNowStamp) + app + version + srcret_key
                token = hashlib.md5(dt.encode(encoding='UTF-8')).hexdigest()
                logger.info("生成token：" + token)
                lgn.token = token
                lgn.expTime = datetime.datetime.now() + datetime.timedelta(days=15)
                dbhandle.session.commit()
                res_data = {"code": code_success, "msg": msg_success, "token": token}
                logger.info('登录返回内容：' + json.dumps(res_data, ensure_ascii=False))
                return res_data
            elif (lgn.token != None) and (re_date < lgn.expTime.strftime('%Y-%m-%d')):
                res_data = {"code": code_success, "msg": msg_success, "token": lgn.token}
                logger.info('登录返回内容：' + json.dumps(res_data, ensure_ascii=False))
                return res_data
            elif (lgn.token != None) and (re_date >= lgn.expTime.strftime('%Y-%m-%d')):
                dt = str(timeNowStamp) + app + version + srcret_key
                token = hashlib.md5(dt.encode(encoding='UTF-8')).hexdigest()
                logger.info("生成token：" + token)
                lgn.token = token
                lgn.expTime = datetime.datetime.now() + datetime.timedelta(days=15)
                dbhandle.session.commit()
                res_data = {"code": code_success, "msg": msg_success, "token": token}
                logger.info('登录返回内容：' + json.dumps(res_data, ensure_ascii=False))
                return res_data
            else:
                res_data = {"code": code_fail, "msg": "未知错误"}
                logger.error('登录返回内容：' + json.dumps(res_data, ensure_ascii=False))
                return res_data


class addApps(Resource):
    """添加应用"""

    def post(self):
        """
        @@@
        #### args

        > {"app":"brainCtl"}

        #### return
        > { "code": code_success, "msg": msg_success, "app": "brainCtl", "appId": "ce037d4c0dfaa9536f98d1ced8bb6e3eac7431cb35cfc30a45e097d6f2606988" }
        @@@
        """
        token = request.headers['token']
        rqutdata = request.get_data()
        lgn = userlogin.query.filter_by(username="admin").first()
        if token == lgn.token:
            aatd = json.loads(rqutdata)
            logger.info('添加应用接收到的参数：' + json.dumps(aatd, ensure_ascii=False))
            app = aatd["app"]
            id = hashlib.sha256(app.encode()).hexdigest()
            data = appManage(id=id, app=app)
            dbhandle.session.add(data)
            dbhandle.session.commit()
            res_data = {"code": code_success, "msg": msg_success, "app": app, "appId": id}
            logger.info('添加应用的返回内容：' + json.dumps(res_data, ensure_ascii=False))
            return res_data
        else:
            res_data = {"code": code_tokenError, "msg": msg_tokenError}
            logger.error('添加应用的返回内容：' + json.dumps(res_data, ensure_ascii=False))
            return res_data


class startTaskTest(Resource):
    """测试任务"""

    def get(self):
        """
        @@@
        #### args

        > appId: 8872a4c00d90bd2fdcfc04784c1de82e637f1b82f21e13f979a76e50fea14d0a

        #### return
        > {"code": code_mde, "msg": "未检测到测试任务", "runningFlag": "False"}
        @@@
        """
        token = request.headers['token']
        lgn = userlogin.query.filter_by(username="admin").first()
        if token == lgn.token:
            appId = request.args.get("appId")
            uuid = request.args.get("uuid")
            type = request.args.get("type")
            am = appManage.query.filter_by(id=appId).first()
            if am == None:
                res_data = {"code": code_fail, "msg": "缺少appId参数或请求的appId不合法"}
                logger.info('查询测试任务返回内容：' + json.dumps(res_data, ensure_ascii=False))
                return res_data
            else:
                if type == 'android' or type == 'ios':
                    if uuid == None or uuid == "":
                        res_data = {"code": code_fail, "msg": "缺少uuid参数"}
                        logger.info('查询测试任务返回内容：' + json.dumps(res_data, ensure_ascii=False))
                        return res_data
                    else:
                        token = loginServer()
                        headers = {"Authorization": "Bearer " + token}
                        baseuri, deviceInfo = parsedvscf(baseDir)
                        deviceInfo_uri = baseuri + deviceInfo
                        status = 'available'
                        params = {'uuid': uuid, 'status': status}
                        logger.info("查询设备信息参数：" + json.dumps(params, ensure_ascii=False))
                        response = requests.get(url=deviceInfo_uri, headers=headers,
                                                params=params)
                        res = response.text
                        res = json.loads(res)
                        logger.info("查询设备信息返回内容：" + json.dumps(res, ensure_ascii=False))
                        if res['results'] == []:
                            res_data = {"code": code_fail, "msg": "uuid请求不合法"}
                            logger.info('查询测试任务返回内容：' + json.dumps(res_data, ensure_ascii=False))
                            return res_data
                old = onLineDete.query.filter_by(id=appId).first()
                lastReqTime = datetime.datetime.now()
                if old == None:
                    data = onLineDete(id=appId, lastReqTime=lastReqTime)
                    dbhandle.session.add(data)
                    dbhandle.session.commit()
                else:
                    dbhandle.session.query(onLineDete).filter_by(id=appId).update({'lastReqTime': lastReqTime})
                    dbhandle.session.commit()
                dt = startTestTask.query.filter_by(runningFlag="True").first()
                if dt == None:
                    res_data = {"code": code_mde, "msg": "未检测到测试任务", "runningFlag": "False"}
                    logger.info('查询测试任务返回内容：' + json.dumps(res_data, ensure_ascii=False))
                    return res_data
                else:
                    res_data = {"code": code_success, "msg": "接收到测试任务", "optUser": dt.optUser, "taskId": dt.testTask_id,
                                "taskName": dt.taskName, "runningFlag": dt.runningFlag, "runMode": dt.runMode,"runNum": dt.runNum,
                                "repeatMode": dt.repeatMode,"runTime": dt.runTime, "reRunFlag": dt.reRunFlag, "createTime": str(dt.createTime)}
                    logger.info('查询测试任务返回内容：' + json.dumps(res_data, ensure_ascii=False))
                    return res_data
        else:
            res_data = {"code": code_tokenError, "msg": msg_tokenError}
            logger.error('查询测试任务返回内容：' + json.dumps(res_data, ensure_ascii=False))
            return res_data

    def post(self):
        """
        @@@
        #### args

        > {"project_id": 1, "testTask_id": 697, "taskName": "lilin_CP_2020-11-16 09:54:20", "opUser": "lilin", "runFlag": "True",
        "runMode": "2", "runPlatform": "1", "runNum": 3, "repeatMode": "02", "runTime": "", "reRunFlag": "True"}

        #### return
        > {"code": code_success, "msg": "提交测试任务成功", "runningFlag": "True"}
        @@@
        """
        token = request.headers['token']
        rqutdata = request.get_data()
        lgn = userlogin.query.filter_by(username="admin").first()
        if token == lgn.token:
            if "=" in str(request.get_data()):
                reqdata = {}
                rqtdata = request.get_data().decode('utf-8', 'ignore')
                if "&" in rqtdata:
                    reqlist = rqtdata.split('&')
                    for rql in reqlist:
                        reqdt = "".join(rql)
                        reqdtlist = reqdt.split('=')
                        reqdata["".join(reqdtlist[0])] = "".join(reqdtlist[-1])
                else:
                    reqdtlist = rqtdata.split('=')
                    reqdata["".join(reqdtlist[0])] = "".join(reqdtlist[-1])
                rqutdata = json.dumps(reqdata)
            sttd = json.loads(rqutdata)
            logger.info('启动测试任务接收到的参数：' + json.dumps(sttd, ensure_ascii=False))
            project_id = sttd['project_id']
            testTask_id = sttd['testTask_id']
            taskName = sttd['taskName']
            optUser = sttd['opUser']
            runMode = sttd['runMode']
            runNum = sttd['runNum']
            runFlag = sttd['runFlag']
            repeatMode = sttd['repeatMode']
            runTime = sttd['runTime']
            reRunFlag = sttd['reRunFlag']
            createTime = datetime.datetime.now()
            updateTime = datetime.datetime.now()
            if runFlag == 'unRun':
                dt = startTestTask.query.filter_by(runningFlag="True").first()
                if dt == None:
                    data = startTestTask(project_id=project_id, testTask_id=testTask_id, taskName=taskName,
                                         optUser=optUser, runMode=runMode, runNum=runNum,
                                         repeatMode=repeatMode, runTime=runTime, runningFlag="True",
                                         reRunFlag=reRunFlag,
                                         createTime=createTime, updateTime=updateTime)
                    dbhandle.session.add(data)
                    dbhandle.session.commit()
                    # dt = startTestTask.query.filter_by(runningFlag="True").first()
                    # print(dt.runningFlag)
                    res_data = {"code": code_success, "msg": "提交测试任务成功", "runningFlag": "True"}
                    logger.info('启动测试任务返回内容：' + json.dumps(res_data, ensure_ascii=False))
                    return res_data
                else:
                    res_data = {"code": code_mde, "msg": "当前有测试任务在执行，请稍后提交任务", "runningFlag": "False"}
                    logger.info('启动测试任务返回内容：' + json.dumps(res_data, ensure_ascii=False))
                    return res_data
            else:
                res_data = {"code": code_mde, "msg": "未提交测试任务", "runningFlag": "False"}
                logger.info('启动测试任务返回内容：' + json.dumps(res_data, ensure_ascii=False))
                return res_data
        else:
            res_data = {"code": code_tokenError, "msg": msg_tokenError}
            logger.error('启动测试任务返回内容：' + json.dumps(res_data, ensure_ascii=False))
            return res_data


class ifOnLineDete(Resource):
    """应用或者设备在线检查"""

    def get(self):
        """
        @@@
        #### args

        > appId: 8872a4c00d90bd2fdcfc04784c1de82e637f1b82f21e13f979a76e50fea14d0a

        #### return
        > { "code": code_success, "msg": msg_success, "appId": "ce037d4c0dfaa9536f98d1ced8bb6e3eac7431cb35cfc30a45e097d6f2606988", "lastReqTime": "2020-11-17 10:22:30", "onLine": "true" }
        @@@
        """
        token = request.headers['token']
        lgn = userlogin.query.filter_by(username="admin").first()
        if token == lgn.token:
            appId = request.args.get("appId")
            am = appManage.query.filter_by(id=appId).first()
            if am == None:
                res_data = {"code": code_fail, "msg": "缺少appId参数或请求的appId不合法"}
                logger.error('检测appId：%s的返回内容：%s' % (appId, json.dumps(res_data, ensure_ascii=False)))
                return res_data
            else:
                old = onLineDete.query.filter_by(id=appId).first()
                if old != None:
                    lastReqTime = old.lastReqTime
                    timeNowStamp = time.mktime(datetime.datetime.now().timetuple())
                    lastReqTimeStamp = time.mktime(lastReqTime.timetuple())
                    dt = startTestTask.query.filter_by(runningFlag="True").first()
                    if dt != None:
                        onLine = "true"
                    else:
                        if abs(int(timeNowStamp) - int(lastReqTimeStamp)) <= 10:
                            onLine = "true"
                        else:
                            onLine = "false"
                    # app = am.app
                    # if "_" in app:
                    #     appnd = app.split('_')
                    #     nodeId = int(appnd[1])
                    #     niol = nodeIdOnline.query.filter_by(nodeId=nodeId).first()
                    #     if niol == None:
                    #         data = nodeIdOnline(nodeId=nodeId, status=onLine)
                    #         dbhandle.session.add(data)
                    #         dbhandle.session.commit()
                    #     else:
                    #         updateTime = datetime.datetime.now()
                    #         dbhandle.session.query(nodeIdOnline).filter_by(nodeId=nodeId).update({'status': onLine, 'updateTime':updateTime})
                    #         dbhandle.session.commit()
                    res_data = {"code": code_success, "msg": msg_success, "appId": appId, "lastReqTime": str(lastReqTime),
                                "onLine": onLine}
                    logger.info('检测appId:%s的返回内容:%s' % (appId, json.dumps(res_data, ensure_ascii=False)))
                    return res_data
                else:
                    res_data = {"code": code_mde, "msg": "应用或设备不在线，请联系管理员", "appId": appId}
                    logger.info('检测appId:%s的返回内容:%s' % (appId, json.dumps(res_data, ensure_ascii=False)))
                    return res_data
        else:
            res_data = {"code": code_tokenError, "msg": msg_tokenError}
            logger.error('获取测试用例执行列表返回内容：' + json.dumps(res_data, ensure_ascii=False))
            return res_data


class getTestcasesRunList(Resource):
    """用例执行列表"""

    def get(self):
        """
        @@@
        #### args

        > project: one

        #### return
        > {
            "data": [
                {
                    "id": 1,
                    "busmodule": "临停车进出场",
                    "caseType": "1",
                    "caseLevel": "1",
                    "caseFile": "test1.py",
                    "caseModule": "test1",
                    "casePcFunction": "test",
                    "caseMobileFunction": "test",
                    "runType": "1",
                    "opUser": "颜晓清",
                    "addTime": "2020-11-13T17:40:39.136512",
                    "casename": 24,
                    "projectGroup": 3,
                    "project": 4
                },
                {
                    "id": 2,
                    "busmodule": "临停车进出场",
                    "caseType": "1",
                    "caseLevel": "1",
                    "caseFile": "test2.py",
                    "caseModule": "test2",
                    "casePcFunction": "test2",
                    "caseMobileFunction": "test2",
                    "runType": "1",
                    "opUser": "颜晓清",
                    "addTime": "2020-11-13T17:40:39.194939",
                    "casename": 25,
                    "projectGroup": 3,
                    "project": 4
                }
            ],
            "code": code_success,
            "message": "success"
        }
        @@@
        """
        token = request.headers['token']
        lgn = userlogin.query.filter_by(username="admin").first()
        if token == lgn.token:
            token = loginServer()
            url, project_id = parsegtcrlcf(baseDir)
            dt = startTestTask.query.filter_by(runningFlag="True").first()
            taskId = dt.testTask_id
            headers = {"Authorization": "Bearer " + token}
            params = {'project_id': project_id, 'taskId': taskId}
            logger.info('获取测试用例执行列表参数：' + json.dumps(params, ensure_ascii=False))
            response = requests.get(url=url, headers=headers, params=params)
            res = response.text
            res = json.loads(res)
            logger.info('获取测试用例执行列表返回内容：' + json.dumps(res, ensure_ascii=False))
            caseTotal = len(res["data"])
            updateTime = datetime.datetime.now()
            dbhandle.session.query(startTestTask).filter_by(testTask_id=taskId).update(
                {'caseTotal': caseTotal, 'updateTime': updateTime})
            dbhandle.session.commit()
            return res
        else:
            res_data = {"code": code_tokenError, "msg": msg_tokenError}
            logger.error('获取测试用例执行列表返回内容：' + json.dumps(res_data, ensure_ascii=False))
            return res_data

class updateTestTask(Resource):
    """更新测试任务"""

    def post(self):
        """
        @@@
        #### args

        >{"taskRunFlag": "False", "ratio": "100.00%", "isDisplayReRun": "True"}

        #### return
        > {"id": 698, "taskName": "lilin_CP_2020-11-16 09:54:20", "projectGroup_id": 1, "project_id": 1, "taskRunFlag": "False", "optUser": "lilin", "runMode": "2", "runPlatform": null, "runNum": 3, "repeatMode": "02", "runTime": "", "reRunFlag": "True", "ratio": "100.00%", "isDisplayReRun": "True", "logsDir": null, "capturesDir": null, "reportDir": null, "createTime": "2020-11-16T15:32:15.110480", "modifyTime": "2020-11-16T15:34:48.026472"}
        @@@
        """
        token = request.headers['token']
        rqutdata = request.get_data()
        uttdata = json.loads(rqutdata)
        taskId = uttdata['taskId']
        taskRunFlag = uttdata['taskRunFlag']
        ratio = uttdata['ratio']
        lgn = userlogin.query.filter_by(username="admin").first()
        if token == lgn.token:
            token = loginServer()
            headers = {'Content-Type': 'application/json;charset=utf-8', "Authorization": "Bearer " + token}
            thl_uri = parseutttcf(baseDir)
            testTask = startTestTask.query.filter_by(runningFlag="True").first()
            testTask_id = testTask.testTask_id
            if int(taskId) == testTask_id:
                if ratio != "-0.00%":
                    updateTime = datetime.datetime.now()
                    dbhandle.session.query(startTestTask).filter_by(testTask_id=testTask_id).update(
                        {'runningFlag': taskRunFlag, "ratio": ratio, 'updateTime': updateTime})
                    dbhandle.session.commit()
                    thl_uri = thl_uri + str(testTask_id) + '/'
                    isDisplayReRun = "False"
                    if ratio != '100.00%' and taskRunFlag != 'Destroy':
                        isDisplayReRun = "True"
                    data = {"taskRunFlag": taskRunFlag, "ratio": ratio, "isDisplayReRun": isDisplayReRun}
                    logger.info('更新测试任务结果参数：' + json.dumps(data, ensure_ascii=False))
                    response = requests.put(thl_uri, headers=headers,
                                            data=json.dumps(data, ensure_ascii=False).encode("utf-8"))
                    res = response.text
                    res = json.loads(res)
                    logger.info('更新测试任务结果返回内容：' + json.dumps(res, ensure_ascii=False))
                    if res['taskRunFlag'] == taskRunFlag:
                        res_data = {"code": code_success, "msg": "更新测试任务成功"}
                        logger.info('更新测试任务结果:' + json.dumps(res_data, ensure_ascii=False))
                        return res_data
                    else:
                        res_data = {"code": 6001, "msg": "未知错误"}
                        logger.error('更新测试任务结果:' + json.dumps(res_data, ensure_ascii=False))
                        return res_data
                else:
                    src_file = ""
                    for root, dirs, files in os.walk(lastReport_dir):
                        for file in files:
                            src_file = os.path.join(root, file)
                            # print(src_file)
                    sf = src_file.split("\\")
                    preTestTask_id = int(sf[-2])
                    logger.info("上次的任务Id：" + str(preTestTask_id))
                    uri = ""
                    if uttdata['caseTotal'] == None:
                        uri = thl_uri + str(preTestTask_id) + '/'
                        predata = {"isDisplayReRun": "False"}
                    else:
                        uri = thl_uri + str(taskId) + '/'
                        predata = {"casesTotal": uttdata['caseTotal']}
                    response = requests.put(uri, headers=headers,
                                            data=json.dumps(predata, ensure_ascii=False).encode("utf-8"))
                    res = response.text
                    res = json.loads(res)
                    logger.info('更新上一次测试任务结果返回内容：' + json.dumps(res, ensure_ascii=False))

                    thl_uri = thl_uri + str(testTask_id) + '/'
                    data = {"taskRunFlag": taskRunFlag}
                    logger.info('更新测试任务结果参数：' + json.dumps(data, ensure_ascii=False))
                    response = requests.put(thl_uri, headers=headers,
                                            data=json.dumps(data, ensure_ascii=False).encode("utf-8"))
                    res = response.text
                    res = json.loads(res)
                    logger.info('更新测试任务结果返回内容：' + json.dumps(res, ensure_ascii=False))
                    return res
            else:
                res_data = {"code": code_fail, "msg": "找不到对应任务"}
                logger.error('更新测试任务结果:' + json.dumps(res_data, ensure_ascii=False))
                return res_data
        else:
            res_data = {"code": code_tokenError, "msg": "不支持的请求类型或者token过期"}
            return res_data

class queryPersonTask(Resource):
    """查询个人任务"""

    def post(self):
        rqutdata = request.get_data()
        sttd = json.loads(rqutdata)
        headers = sttd['headers']
        token = headers['token']
        dt = sttd['params']
        lgn = userlogin.query.filter_by(username="admin").first()
        if token == lgn.token:
            logger.info('查询个人任务状态参数：' + json.dumps(sttd, ensure_ascii=False))
            project_id = dt['project_id']
            testTask_id = dt['testTask_id']
            optUser = dt['optUser']
            type = dt['type']
            if type == "destroy":
                dt = startTestTask.query.filter_by(runningFlag="True").first()
                if dt == None:
                    res_data = {"code": code_success, "msg": "操作成功，任务已结束"}
                    logger.info('查询个人任务状态返回内容：' + json.dumps(res_data, ensure_ascii=False))
                    return res_data
                else:
                    if dt.project_id == int(project_id) and dt.testTask_id == testTask_id and dt.optUser == optUser:
                        res_data = {"code": code_fail, "msg": "操作成功，任务正在执行"}
                    else:
                        res_data = {"code": code_success, "msg": "操作成功，任务已结束"}
                    logger.info('查询个人任务状态返回内容：' + json.dumps(res_data, ensure_ascii=False))
                    return res_data
            else:
                dt = startTestTask.query.filter_by(testTask_id=testTask_id).first()
                if dt == None:
                    res_data = {"code": code_fail, "msg": "查询无此任务"}
                    logger.info('查询个人任务状态返回内容：' + json.dumps(res_data, ensure_ascii=False))
                    return res_data
                else:
                    res_data = {"code": code_success, "msg": msg_success,"data":{"taskId":dt.testTask_id,"taskRunFlag":dt.runningFlag,"ratio":dt.ratio,"reRunFlag":dt.reRunFlag}}
                    logger.info('查询个人任务状态返回内容：' + json.dumps(res_data, ensure_ascii=False))
                    return res_data
        else:
            res_data = {"code": code_tokenError, "msg": "不支持的请求类型或者token过期"}
            return res_data


class destroyTask(Resource):
    """撤销任务"""

    def post(self):
        rqutdata = request.get_data()
        data = json.loads(rqutdata)
        headers = data['headers']
        dtp = data["params"]
        token = headers["token"]
        lgn = userlogin.query.filter_by(username="admin").first()
        if token == lgn.token:
            logger.info('平台撤销任务参数：' + json.dumps(dtp, ensure_ascii=False))
            optUser = dtp["optUser"]
            taskId = dtp["testTask_id"]
            dt = startTestTask.query.filter_by(runningFlag="True").first()
            if optUser == dt.optUser and taskId == dt.testTask_id:
                nidy = taskIdDestory.query.filter_by(taskId=taskId).first()
                if nidy == None:
                    data = taskIdDestory(taskId=taskId)
                    dbhandle.session.add(data)
                    dbhandle.session.commit()
                else:
                    updateTime = datetime.datetime.now()
                    dbhandle.session.query(taskIdDestory).filter_by(taskId=taskId).update({'destoryFlag': "todo", 'updateTime': updateTime})
                    dbhandle.session.commit()
                # with open(cachedir, "w", encoding="utf-8") as cc:
                #     cc.write("1")

                timeOut = 120
                while timeOut >= 0:
                    nidy = taskIdDestory.query.filter_by(taskId=taskId).first()
                    if nidy != None:
                        destoryFlag = nidy.destoryFlag
                        if destoryFlag == "done":
                            res_data = {"code": code_success, "msg": msg_success}
                            logger.info('平台撤销任务返回内容：' + json.dumps(res_data, ensure_ascii=False))
                            return res_data
                        else:
                            time.sleep(1)
                            timeOut -= 1
                    else:
                        time.sleep(1)
                        timeOut -= 1
                    # with open(cachedir, "r", encoding="utf-8") as cc:
                    #     fg = cc.read()
                    #     logger.info("撤销标记：" + fg)
                    # if fg == "2":
                    #     res_data = {"code": code_success, "msg": msg_success}
                    #     logger.info('撤销任务返回内容：' + json.dumps(res_data, ensure_ascii=False))
                    #     return res_data
                    # else:
                    #     time.sleep(1)
                    #     timeOut -= 1
                res_data = {"code": code_fail, "msg": "撤销任务失败，请稍后重试"}
                logger.info('平台撤销任务返回内容：' + json.dumps(res_data, ensure_ascii=False))
                return res_data
        else:
            res_data = {"code": code_tokenError, "msg": "不支持的请求类型或者token过期"}
            logger.info('平台撤销任务返回内容：' + json.dumps(res_data, ensure_ascii=False))
            return res_data

class updateOldTestTask(Resource):
    """更新测试任务"""

    def post(self):
        """
        @@@
        #### args

        >{"taskRunFlag": "False", "ratio": "100.00%", "isDisplayReRun": "True"}

        #### return
        > {"id": 698, "taskName": "lilin_CP_2020-11-16 09:54:20", "projectGroup_id": 1, "project_id": 1, "taskRunFlag": "False", "optUser": "lilin", "runMode": "2", "runPlatform": null, "runNum": 3, "repeatMode": "02", "runTime": "", "reRunFlag": "True", "ratio": "100.00%", "isDisplayReRun": "True", "logsDir": null, "capturesDir": null, "reportDir": null, "createTime": "2020-11-16T15:32:15.110480", "modifyTime": "2020-11-16T15:34:48.026472"}
        @@@
        """
        token = request.headers['token']
        rqutdata = request.get_data()
        uttdata = json.loads(rqutdata)
        taskId = uttdata['taskId']
        taskRunFlag = uttdata['taskRunFlag']
        lgn = userlogin.query.filter_by(username="admin").first()
        if token == lgn.token:
            testTask = startTestTask.query.filter_by(runningFlag="True").first()
            testTask_id = testTask.testTask_id
            if int(taskId) == testTask_id:
                updateTime = datetime.datetime.now()
                dbhandle.session.query(startTestTask).filter_by(testTask_id=testTask_id).update(
                    {'runningFlag': taskRunFlag, 'updateTime': updateTime})
                dbhandle.session.commit()
                res_data = {"code": code_success, "msg": "更新历史测试任务成功"}
                logger.info('更新测试任务结果:' + json.dumps(res_data, ensure_ascii=False))
                return res_data
            else:
                res_data = {"code": code_fail, "msg": "找不到该任务"}
                logger.error('更新历史测试任务结果:' + json.dumps(res_data, ensure_ascii=False))
                return res_data
        else:
            res_data = {"code": code_tokenError, "msg": "不支持的请求类型或者token过期"}
            return res_data

class caseidsBranchClean(Resource):
    """清除子进程对应的用例表"""

    def post(self):
        """
        @@@
        #### args

        >{"taskRunFlag": "False", "ratio": "100.00%", "isDisplayReRun": "True"}

        #### return
        > {"id": 698, "taskName": "lilin_CP_2020-11-16 09:54:20", "projectGroup_id": 1, "project_id": 1, "taskRunFlag": "False", "optUser": "lilin", "runMode": "2", "runPlatform": null, "runNum": 3, "repeatMode": "02", "runTime": "", "reRunFlag": "True", "ratio": "100.00%", "isDisplayReRun": "True", "logsDir": null, "capturesDir": null, "reportDir": null, "createTime": "2020-11-16T15:32:15.110480", "modifyTime": "2020-11-16T15:34:48.026472"}
        @@@
        """
        # token = request.headers['token']
        # lgn = userlogin.query.filter_by(username="admin").first()
        # if token == lgn.token:
        try:
            rqutdata = request.get_data()
            uttdata = json.loads(rqutdata)
            logger.info('清除子进程对应用例参数:' + json.dumps(uttdata, ensure_ascii=False))
            pid = uttdata['pid']
            nodeId = uttdata['nodeId']
            conn = pymysql.connect(host=host, user=username, password=password, database=dbname, port=int(dbport))
            if pid == "":
                sql = "truncate table cases_branch"
                truncate(conn,sql)
            else:
                result = casesBranch.query.filter_by(pid=pid).first()
                if result == None:
                    res_data = {"code": code_fail, "msg": "操作失败,记录不存在"}
                    logger.info('清除子进程对应用例表返回内容:' + json.dumps(res_data, ensure_ascii=False))
                    return res_data
                else:
                    sql = "delete from cases_branch where pid = '%s' and nodeId = '%s'" % (pid,nodeId)
                    delete(conn,sql)
            sqlcls(conn)
            res_data = {"code": code_success, "msg": msg_success}
            logger.info('清除子进程对应用例表返回内容:' + json.dumps(res_data, ensure_ascii=False))
            return res_data
        except BaseException as msg:
            res_data = {"code": code_fail, "msg": "操作失败，"+ msg}
            logger.error('清除子进程对应用例表返回内容:' + json.dumps(res_data, ensure_ascii=False))
            return res_data
            # else:
            #     res_data = {"code": code_tokenError, "msg": "不支持的请求类型或者token过期"}
            #     return res_data

class caseidsBranch(Resource):
    """子进程对应的用例"""

    def get(self):
        # token = request.headers['token']
        pid = request.args.get("pid")
        nodeId = request.args.get("nodeId")
        # lgn = userlogin.query.filter_by(username="admin").first()
        # if token == lgn.token:
        result = casesBranch.query.filter_by(pid=pid,nodeId=int(nodeId)).first()
        if result != None:
            res_data = {"code": code_success, "msg": msg_success,"data":{"pid":result.pid,"nodeId":result.nodeId,"caseids":result.caseids}}
            logger.info('查询子进程对应用例返回内容:' + json.dumps(res_data, ensure_ascii=False))
            return res_data
        else:
            res_data = {"code": code_fail, "msg": "操作失败，记录不存在"}
            logger.error('获取测试用例执行列表返回内容：' + json.dumps(res_data, ensure_ascii=False))
            return res_data

    def post(self):
        """
        @@@
        #### args

        >{"taskRunFlag": "False", "ratio": "100.00%", "isDisplayReRun": "True"}

        #### return
        > {"id": 698, "taskName": "lilin_CP_2020-11-16 09:54:20", "projectGroup_id": 1, "project_id": 1, "taskRunFlag": "False", "optUser": "lilin", "runMode": "2", "runPlatform": null, "runNum": 3, "repeatMode": "02", "runTime": "", "reRunFlag": "True", "ratio": "100.00%", "isDisplayReRun": "True", "logsDir": null, "capturesDir": null, "reportDir": null, "createTime": "2020-11-16T15:32:15.110480", "modifyTime": "2020-11-16T15:34:48.026472"}
        @@@
        """
        try:
            # token = request.headers['token']
            rqutdata = request.get_data()
            uttdata = json.loads(rqutdata)
            logger.info('提交子进程对应用例参数:' + json.dumps(uttdata, ensure_ascii=False))
            pid = uttdata['pid']
            nodeId = uttdata['nodeId']
            caseids = uttdata['caseids']
            # lgn = userlogin.query.filter_by(username="admin").first()
            # if token == lgn.token:
                # conn = pymysql.connect(host=host, user=username, password=password, database=dbname, port=int(port))
                # sql = "truncate table cases_branch"
                # truncate(conn,sql)
                # print(pid,caseids)
            data = casesBranch(pid=pid,nodeId=nodeId,caseids=str(caseids))
            dbhandle.session.add(data)
            dbhandle.session.commit()
            res_data = {"code": code_success, "msg": msg_success}
            logger.info('提交子进程对应用例返回内容:' + json.dumps(res_data, ensure_ascii=False))
            return res_data
        except BaseException as msg:
            res_data = {"code": code_fail, "msg": "操作失败，"+ msg}
            logger.error('提交子进程对应用例返回内容:' + json.dumps(res_data, ensure_ascii=False))
            return res_data
        # else:
        #     res_data = {"code": code_tokenError, "msg": "不支持的请求类型或者token过期"}
        #     return res_data

class allureDete(Resource):
    def get(self):
        token = request.headers.get("token")
        app = request.args.get("app")
        # print(token, app)
        # rqutdata = request.get_data()
        # uttdata = json.loads(rqutdata)
        # print(uttdata)
        # headers = uttdata["headers"]
        # token = headers["token"]
        # app = uttdata["params"]["app"]
        lgn = userlogin.query.filter_by(username="admin").first()
        if token == lgn.token:
            allureIP, allurePort = parseAppcf(baseDir)
            allureStatus = "false"
            if app == "allure":
                try:
                    tn = telnetlib.Telnet(allureIP, int(allurePort), 3)
                    allureStatus = "true"
                except BaseException as msg:
                    logger.error(msg)
            else:
                res_data = {"code": code_fail, "msg": "操作失败,app不存在"}
                return res_data

            res_data = {"code": code_success, "msg": msg_success, "allureStatus": allureStatus}
            logger.info('allure在线检查返回内容：' + json.dumps(res_data, ensure_ascii=False))
            return res_data
        else:
            res_data = {"code": code_tokenError, "msg": msg_tokenError}
            logger.error('allure在线检查返回内容：' + json.dumps(res_data, ensure_ascii=False))
            return res_data

class taskProcess(Resource):
    def get(self):
        token = request.args.get("token")
        lgn = userlogin.query.filter_by(username="admin").first()
        if token == lgn.token:
            successedTotal, failedTotal, pengdingTotal = 0, 0, 0
            dt = dbhandle.session.query(caseRunningStatic).filter_by(step=3, result="passed").all()
            successedTotal = len(dt)
            # print(successedTotal)
            dt = dbhandle.session.query(caseRunningStatic).filter_by(result="failed").all()
            failedTotal = len(dt)
            # print(failedTotal)
            dt = startTestTask.query.filter_by(runningFlag="True").first()
            if dt != None:
                pendingTotal = (dt.caseTotal * dt.runNum) - (successedTotal + failedTotal)
                process = str('%.2f' % (((successedTotal + failedTotal) / (dt.caseTotal * dt.runNum)) * 100)) + '%'
                res_data = {"code": code_success, "msg": msg_success,
                            "data": {"successedTotal": successedTotal, "failedTotal": failedTotal,
                                     "pendingTotal": pendingTotal, "process": process}}
                updateTime = datetime.datetime.now()
                dbhandle.session.query(startTestTask).filter_by(testTask_id=dt.testTask_id).update(
                    {'successedTotal': successedTotal, 'failedTotal': failedTotal, 'pendingTotal': pendingTotal,
                     'process': process, 'updateTime': updateTime})
                dbhandle.session.commit()
            else:
                process = "100.00%"
                pendingTotal = 0
                res_data = {"code": code_success, "msg": msg_success,
                            "data": {"successedTotal": successedTotal, "failedTotal": failedTotal,
                                     "pendingTotal": pendingTotal, "process": process}}
                dt = dbhandle.session.query(startTestTask).order_by(startTestTask.updateTime.desc()).first()
                updateTime = datetime.datetime.now()
                dbhandle.session.query(startTestTask).filter_by(testTask_id=dt.testTask_id).update(
                    {'successedTotal': successedTotal, 'failedTotal': failedTotal, 'pendingTotal': pendingTotal,
                     'process': process, 'updateTime': updateTime})
                dbhandle.session.commit()
            logger.info('获取任务进度返回内容：' + json.dumps(res_data, ensure_ascii=False))
            return res_data
        else:
            res_data = {"code": code_tokenError, "msg": msg_tokenError}
            logger.error('获取任务进度返回内容：' + json.dumps(res_data, ensure_ascii=False))
            return res_data

    def post(self):
        rqutdata = request.get_data()
        uttdata = json.loads(rqutdata)
        headers = uttdata["headers"]
        token = headers["token"]
        lgn = userlogin.query.filter_by(username="admin").first()
        if token == lgn.token:
            params = uttdata["params"]
            caseNo = params["caseNo"]
            when = params["when"]
            status = params["status"]
            if when == "setup":
                step = 1
            elif when == "call":
                step = 2
            elif when == "teardown":
                step = 3
            else:
                step = 0
            result = ""
            dt = dbhandle.session.query(caseRunningStatic).filter_by(caseNo=caseNo).order_by(
                caseRunningStatic.updateTime.desc()).first()
            if dt == None:
                result = status
                updateTime = datetime.datetime.now()
                data = caseRunningStatic(caseNo=caseNo, when=when, step=step,
                                         status=status, result=result, updateTime=updateTime)
                dbhandle.session.add(data)
                dbhandle.session.commit()
                res_data = {"code": code_success, "msg": msg_success}
                logger.info('提交任务进度返回内容：' + json.dumps(res_data, ensure_ascii=False))
                return res_data
            elif dt.when != when and dt.step != step and when != "setup":
                if dt.status != "passed":
                    result = "failed"
                else:
                    result = status
                updateTime = datetime.datetime.now()
                dbhandle.session.query(caseRunningStatic).filter_by(id=dt.id).update(
                    {'when': when, 'step': step, 'status': status, 'result': result, 'updateTime': updateTime})
                dbhandle.session.commit()
                res_data = {"code": code_success, "msg": msg_success}
                logger.info('提交任务进度返回内容：' + json.dumps(res_data, ensure_ascii=False))
                return res_data
            elif dt.when == when and dt.step == step and when == "setup":
                result = status
                updateTime = datetime.datetime.now()
                data = caseRunningStatic(caseNo=caseNo, when=when, step=step,
                                         status=status, result=result, updateTime=updateTime)
                dbhandle.session.add(data)
                dbhandle.session.commit()
                res_data = {"code": code_success, "msg": msg_success}
                logger.info('提交任务进度返回内容：' + json.dumps(res_data, ensure_ascii=False))
                return res_data
            elif dt.when != when and dt.step != step and when == "setup":
                result = status
                updateTime = datetime.datetime.now()
                data = caseRunningStatic(caseNo=caseNo, when=when, step=step,
                                         status=status, result=result, updateTime=updateTime)
                dbhandle.session.add(data)
                dbhandle.session.commit()
                res_data = {"code": code_success, "msg": msg_success}
                logger.info('提交任务进度返回内容：' + json.dumps(res_data, ensure_ascii=False))
                return res_data
            else:
                res_data = {"code": code_fail, "msg": msg_fail}
                logger.error('提交任务进度返回内容：' + json.dumps(res_data, ensure_ascii=False))
                return res_data
        else:
            res_data = {"code": code_tokenError, "msg": msg_tokenError}
            logger.error('提交任务进度返回内容：' + json.dumps(res_data, ensure_ascii=False))
            return res_data

class modules(Resource):
    def get(self):
        token = request.headers.get("token")
        lgn = userlogin.query.filter_by(username="admin").first()
        if token == lgn.token:
            cmd = f'python {PRO_PATH}\\testCases\\cases_sync.py modules'
            os.system(cmd)
            time.sleep(3)
            modules_normal_sql = 'select * from modules_normal'
            conn = sqlConnect(host,username,password,dbname,dbport)
            modules_normal_rows = selectAll(conn, modules_normal_sql)
            modulesSuccess = []
            res_data = {}
            for md in modules_normal_rows:
                module = {}
                module['id'] = md[0]
                module['module'] = md[1]
                module['path'] = md[2]
                module['status'] = md[3]
                modulesSuccess.append(module)
            modules_unusual_sql = 'select * from modules_unusual'
            modules_unusual_rows = selectAll(conn, modules_unusual_sql)
            modulesFail = []
            for md in modules_unusual_rows:
                module = {}
                module['id'] = md[0]
                module['module'] = md[1]
                module['path'] = md[2]
                module['status'] = md[3]
                modulesFail.append(module)
            res_data['code'] = code_success
            res_data['msg'] = msg_success
            res_data['modulesSuccess'] = modulesSuccess
            res_data['modulesFail'] = modulesFail
            sqlcls(conn)
            logger.info('获取业务模块返回内容：' + json.dumps(res_data, ensure_ascii=False))
            return res_data
        else:
            res_data = {"code": code_tokenError, "msg": msg_tokenError}
            logger.error('获取业务模块返回内容：' + json.dumps(res_data, ensure_ascii=False))
            return res_data

    def post(self):
        rqutdata = request.get_data()
        uttdata = json.loads(rqutdata)
        headers = request.headers
        token = headers["token"]
        modulesSuccess = uttdata["modulesSuccess"]
        lgn = userlogin.query.filter_by(username="admin").first()
        if token == lgn.token:
            # 测试代码
            # modulesSuccess = {
            #     "modulesSuccess": [
            #         {
            #             "id": 1,
            #             "module": "组织管理",
            #             "path": "org",
            #             "status": "1"
            #         },
            #         {
            #             "id": 2,
            #             "module": "用户管理",
            #             "path": "user",
            #             "status": "1"
            #         },
            #         {
            #             "id": 3,
            #             "module": "验证码",
            #             "path": "verifyCode",
            #             "status": "1"
            #         }
            #     ],
            #     "modulesFail": []
            # }
            host = '172.16.23.62'
            username = 'root'
            password = 'cpy123456!'
            dbname = 'automation'
            port = 3306
            table = 'busmodule_onemodulesmanage'
            conn = sqlConnect(host,username,password,dbname,port)
            truncate_modules_normal_sql = ["SET foreign_key_checks = 0",f"truncate table {table}","SET foreign_key_checks = 1"]
            for tmns in truncate_modules_normal_sql:
                truncate(conn,tmns)
            modules_normal_sql = f"insert into {table}(id,busmodule,status,createTime,updateTime) values"
            if modulesSuccess != []:
                for ms in modulesSuccess:
                    createTime = datetime.datetime.now()
                    modules_normal_sql += f"('{ms['id']}','{ms['module']}','{ms['status']}','{str(createTime)}','{str(createTime)}'),"
                logger.info(f"正常模块数据sql：{modules_normal_sql.strip(',')}")
                insert(conn,modules_normal_sql.strip(','))
            sqlcls(conn)
            res_data = {}
            res_data['code'] = code_success
            res_data['msg'] = msg_success
            logger.info('提交业务模块返回内容：' + json.dumps(res_data, ensure_ascii=False))
            return res_data
        else:
            res_data = {"code": code_tokenError, "msg": msg_tokenError}
            logger.error('提交业务模块返回内容：' + json.dumps(res_data, ensure_ascii=False))
            return res_data

class cases(Resource):
    def get(self):
        token = request.headers.get("token")
        lgn = userlogin.query.filter_by(username="admin").first()
        if token == lgn.token:
            cmd = f'python {PRO_PATH}\\testCases\\cases_sync.py cases'
            os.system(cmd)
            time.sleep(3)
            cases_normal_sql = 'select * from cases_normal'
            conn = sqlConnect(host, username, password, dbname, dbport)
            cases_normal_rows = selectAll(conn, cases_normal_sql)
            casesSuccess = []
            res_data = {}
            for cs in cases_normal_rows:
                case = {}
                case['caseNo'] = cs[1]
                case['caseTitle'] = cs[2]
                case['caseType'] = cs[4]
                case['caseLevel'] = cs[5]
                case['busModuleId'] = cs[6]
                case['status'] = cs[7]
                casesSuccess.append(case)
            cases_unusual_sql = 'select * from cases_unusual'
            cases_unusual_rows = selectAll(conn, cases_unusual_sql)
            casesFail = []
            for cs in cases_unusual_rows:
                case = {}
                case['caseNo'] = cs[1]
                case['caseTitle'] = cs[2]
                case['caseType'] = cs[4]
                case['caseLevel'] = cs[5]
                case['busModuleId'] = cs[6]
                case['status'] = cs[7]
                casesFail.append(case)
            res_data['code'] = code_success
            res_data['msg'] = msg_success
            res_data['casesSuccess'] = casesSuccess
            res_data['casesFail'] = casesFail
            sqlcls(conn)
            logger.info('获取用例返回内容：' + json.dumps(res_data, ensure_ascii=False))
            return res_data
        else:
            res_data = {"code": code_tokenError, "msg": msg_tokenError}
            logger.error('获取用例返回内容：' + json.dumps(res_data, ensure_ascii=False))
            return res_data

    def post(self):
        rqutdata = request.get_data()
        uttdata = json.loads(rqutdata)
        headers = request.headers
        token = headers["token"]
        casesSuccess = uttdata["casesSuccess"]
        lgn = userlogin.query.filter_by(username="admin").first()
        if token == lgn.token:
            # 测试代码
            # casesSuccess = {
            #     "casesSuccess": [
            #         {
            #             "caseNo": "13001",
            #             "caseTitle": "组长新增组织，罗列所在组织，获取组织详情，添加单一成员，罗列组织成员，剔除成员，修改组织，解散组织，组长罗列组织",
            #             "caseType": "1",
            #             "caseLevel": "1",
            #             "busModuleId": 1,
            #             "status": "1"
            #         },
            #         {
            #             "caseNo": "13002",
            #             "caseTitle": "组长新增组织，组长罗列所在组织，获取组织详情，添加成员，成员登录，成员退出组织，成员罗列所在组织，无成员时组长解散组织，组长罗列组织",
            #             "caseType": "1",
            #             "caseLevel": "1",
            #             "busModuleId": 1,
            #             "status": "1"
            #         },
            #         {
            #             "caseNo": "13003",
            #             "caseTitle": "组长新增组织，组长罗列所在组织，获取组织详情，批量添加成员，有成员时组长解散组织，组长罗列组织",
            #             "caseType": "1",
            #             "caseLevel": "1",
            #             "busModuleId": 1,
            #             "status": "1"
            #         },
            #         {
            #             "caseNo": "10001",
            #             "caseTitle": "获取用户信息，并修改",
            #             "caseType": "1",
            #             "caseLevel": "1",
            #             "busModuleId": 2,
            #             "status": "1"
            #         },
            #         {
            #             "caseNo": "10002",
            #             "caseTitle": "获取用户信息，并修改",
            #             "caseType": "1",
            #             "caseLevel": "1",
            #             "busModuleId": 2,
            #             "status": "1"
            #         }
            #     ],
            #     "casesFail": []
            # }
            host = '172.16.23.62'
            username = 'root'
            password = 'cpy123456!'
            dbname = 'automation'
            port = 3306
            projectGroup_id = 1
            project_id = 2
            table = 'testcases_testcasesonemanage'
            conn = sqlConnect(host, username, password, dbname, port)
            truncate_cases_normal_sql = ["SET foreign_key_checks = 0", f"truncate table {table}",
                                           "SET foreign_key_checks = 1"]
            for tmns in truncate_cases_normal_sql:
                truncate(conn, tmns)
            cases_normal_sql = f"insert into {table}(caseNo,casename,caseType,caseLevel,caseFile,caseModule,casePcFunction,busmodule_id,projectGroup_id,project_id,status,addTime,modifyTime) values"
            if casesSuccess != []:
                for ms in casesSuccess:
                    createTime = datetime.datetime.now()
                    cases_normal_sql += f"('{ms['caseNo']}','{ms['caseTitle']}','{ms['caseType']}','{ms['caseLevel']}','无','无','无','{ms['busModuleId']}',{projectGroup_id},{project_id},'{ms['status']}','{str(createTime)}','{str(createTime)}'),"
                logger.info(f"正常用例数据sql：{cases_normal_sql.strip(',')}")
                insert(conn, cases_normal_sql.strip(','))
            sqlcls(conn)
            res_data = {}
            res_data['code'] = code_success
            res_data['msg'] = msg_success
            logger.info('提交用例返回内容：' + json.dumps(res_data, ensure_ascii=False))
            return res_data
        else:
            res_data = {"code": code_tokenError, "msg": msg_tokenError}
            logger.error('提交用例返回内容：' + json.dumps(res_data, ensure_ascii=False))
            return res_data

restful_api.add_resource(register, '/one/register')
restful_api.add_resource(login, '/one/login')
restful_api.add_resource(addApps, '/one/addApps')
restful_api.add_resource(ifOnLineDete, '/one/ifOnLineDete')
restful_api.add_resource(startTaskTest, '/one/startTaskTest')
restful_api.add_resource(getTestcasesRunList, '/one/getTestcasesRunList')
restful_api.add_resource(updateTestTask, '/one/updateTestTask')
restful_api.add_resource(queryPersonTask, '/one/queryPersonTask')
restful_api.add_resource(taskProcess, '/one/taskProcess')
restful_api.add_resource(destroyTask, '/one/destroyTask')
restful_api.add_resource(updateOldTestTask, '/one/updateOldTestTask')
restful_api.add_resource(caseidsBranch, '/one/casesBranch')
restful_api.add_resource(caseidsBranchClean, '/one/casesBranchClean')
restful_api.add_resource(allureDete, '/one/allureDete')
restful_api.add_resource(modules, '/one/modules')
restful_api.add_resource(cases, '/one/cases')

if __name__ == '__main__':
    # dbhandle.drop_all()
    dbhandle.create_all()
    app.run(host='0.0.0.0', port=18080, debug=True)