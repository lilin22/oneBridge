from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from common.parseconf import parsedbcf
import datetime

app = Flask(__name__)
app.app_context().push()

basePath = r'C:\projects\oneBridge'
baseDir = basePath + '\\base.conf'

data = parsedbcf(baseDir)
host = data['host']
username = data['username']
password = data['password']
dbname = data['dbname']
dbport = data['port']

app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://" + username + ":" + password + "@" + host + ":" + dbport + "/" + dbname + "?charset=utf8"
app.config['SQLALCHEMY_COMMIT_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_POOL_RECYCLE'] = 10
app.config['SQLALCHEMY_POOL_SIZE'] = 500
dbhandle = SQLAlchemy(app)

class userlogin(dbhandle.Model):
    id = dbhandle.Column(dbhandle.Integer,primary_key=True)
    username = dbhandle.Column(dbhandle.String(50),nullable=False)
    password = dbhandle.Column(dbhandle.String(50),nullable=False)
    token = dbhandle.Column(dbhandle.String(500))
    expTime = dbhandle.Column(dbhandle.DateTime, default=datetime.datetime.now() + datetime.timedelta(days=15))
    createTime = dbhandle.Column(dbhandle.DateTime, default=datetime.datetime.now())

    def __repr__(self):
        return '<username %r>' % self.username

class appManage(dbhandle.Model):
    id = dbhandle.Column(dbhandle.String(500),nullable=False,primary_key=True)
    app = dbhandle.Column(dbhandle.String(50),nullable=False)
    createTime = dbhandle.Column(dbhandle.DateTime, default=datetime.datetime.now())

    def __repr__(self):
        return '<app %r>' % self.app

class onLineDete(dbhandle.Model):
    id = dbhandle.Column(dbhandle.String(500),nullable=False,primary_key=True)
    lastReqTime = dbhandle.Column(dbhandle.DateTime,nullable=False)
    createTime = dbhandle.Column(dbhandle.DateTime, default=datetime.datetime.now())

    def __repr__(self):
        return '<id %r>' % self.id

class startTestTask(dbhandle.Model):
    id = dbhandle.Column(dbhandle.Integer, primary_key=True)
    project_id = dbhandle.Column(dbhandle.Integer, nullable=False)
    testTask_id = dbhandle.Column(dbhandle.Integer, nullable=False,unique=True)
    taskName = dbhandle.Column(dbhandle.String(500), nullable=False)
    optUser = dbhandle.Column(dbhandle.String(50), nullable=False)
    runMode = dbhandle.Column(dbhandle.String(10), nullable=False)
    runNum = dbhandle.Column(dbhandle.Integer, nullable=False)
    caseTotal = dbhandle.Column(dbhandle.Integer)
    successedTotal = dbhandle.Column(dbhandle.Integer,default=0)
    failedTotal = dbhandle.Column(dbhandle.Integer,default=0)
    pendingTotal = dbhandle.Column(dbhandle.Integer,default=0)
    process = dbhandle.Column(dbhandle.String(20),default="0.00%")
    repeatMode = dbhandle.Column(dbhandle.String(10), nullable=False)
    runTime = dbhandle.Column(dbhandle.String(50), nullable=True)
    runningFlag = dbhandle.Column(dbhandle.String(50), nullable=False)
    reRunFlag = dbhandle.Column(dbhandle.String(50), nullable=False)
    ratio = dbhandle.Column(dbhandle.String(10))
    createTime = dbhandle.Column(dbhandle.DateTime, default=datetime.datetime.now())
    updateTime = dbhandle.Column(dbhandle.DateTime, default=datetime.datetime.now())

    def __repr__(self):
        return '<optUser %r>' % self.optUser

class casesBranch(dbhandle.Model):
    id = dbhandle.Column(dbhandle.Integer, primary_key=True)
    pid = dbhandle.Column(dbhandle.Integer, nullable=False,unique=True)
    nodeId = dbhandle.Column(dbhandle.Integer)
    caseids = dbhandle.Column(dbhandle.String(1000), nullable=False)
    createTime = dbhandle.Column(dbhandle.DateTime, default=datetime.datetime.now())

    def __repr__(self):
        return '<pid %r>' % self.pid

class casenosByPidByModule(dbhandle.Model):
    id = dbhandle.Column(dbhandle.Integer, primary_key=True)
    pid = dbhandle.Column(dbhandle.String(100), nullable=False)
    module = dbhandle.Column(dbhandle.String(1000), nullable=False)
    caseNos = dbhandle.Column(dbhandle.String(15000), nullable=False)

    def __repr__(self):
        return '<pid %r>' % self.pid

class caseRunningStatic(dbhandle.Model):
    id = dbhandle.Column(dbhandle.Integer, primary_key=True)
    caseNo = dbhandle.Column(dbhandle.String(200), nullable=False,unique=True)
    when = dbhandle.Column(dbhandle.String(50), nullable=False)
    step = dbhandle.Column(dbhandle.Integer, nullable=False)
    status = dbhandle.Column(dbhandle.String(50), nullable=False)
    result = dbhandle.Column(dbhandle.String(50), nullable=False)
    createTime = dbhandle.Column(dbhandle.DateTime, default=datetime.datetime.now())
    updateTime = dbhandle.Column(dbhandle.DateTime, default=datetime.datetime.now())

    def __repr__(self):
        return '<caseNo %r>' % self.caseNo

class modulesNormal(dbhandle.Model):
    id = dbhandle.Column(dbhandle.Integer, primary_key=True)
    busModule = dbhandle.Column(dbhandle.String(100), nullable=False,unique=True)
    path = dbhandle.Column(dbhandle.String(50), nullable=False)
    status = dbhandle.Column(dbhandle.String(50), nullable=False)
    createTime = dbhandle.Column(dbhandle.DateTime, default=datetime.datetime.now())
    updateTime = dbhandle.Column(dbhandle.DateTime, default=datetime.datetime.now())

    def __repr__(self):
        return '<caseNo %r>' % self.busModule

class modulesUnusual(dbhandle.Model):
    id = dbhandle.Column(dbhandle.Integer, primary_key=True)
    busModule = dbhandle.Column(dbhandle.String(100), nullable=False,unique=True)
    path = dbhandle.Column(dbhandle.String(50), nullable=False)
    status = dbhandle.Column(dbhandle.String(50), nullable=False)
    createTime = dbhandle.Column(dbhandle.DateTime, default=datetime.datetime.now())
    updateTime = dbhandle.Column(dbhandle.DateTime, default=datetime.datetime.now())

    def __repr__(self):
        return '<caseNo %r>' % self.busModule

class casesNormal(dbhandle.Model):
    id = dbhandle.Column(dbhandle.Integer, primary_key=True)
    caseNo = dbhandle.Column(dbhandle.String(100), nullable=False,unique=True)
    caseTitle = dbhandle.Column(dbhandle.String(10000), nullable=False)
    caseFile = dbhandle.Column(dbhandle.String(1000), nullable=True)
    caseType = dbhandle.Column(dbhandle.String(50), nullable=False)
    caseLevel = dbhandle.Column(dbhandle.String(50), nullable=False)
    busModuleId = dbhandle.Column(dbhandle.Integer, nullable=False)
    status = dbhandle.Column(dbhandle.String(50), nullable=False)
    createTime = dbhandle.Column(dbhandle.DateTime, default=datetime.datetime.now())
    updateTime = dbhandle.Column(dbhandle.DateTime, default=datetime.datetime.now())

    def __repr__(self):
        return '<caseNo %r>' % self.caseNo

class casesUnusual(dbhandle.Model):
    id = dbhandle.Column(dbhandle.Integer, primary_key=True)
    caseNo = dbhandle.Column(dbhandle.String(100), nullable=False,unique=True)
    caseTitle = dbhandle.Column(dbhandle.String(10000), nullable=False)
    caseFile = dbhandle.Column(dbhandle.String(1000), nullable=True)
    caseType = dbhandle.Column(dbhandle.String(50), nullable=False)
    caseLevel = dbhandle.Column(dbhandle.String(50), nullable=False)
    busModuleId = dbhandle.Column(dbhandle.Integer, nullable=False)
    status = dbhandle.Column(dbhandle.String(50), nullable=False)
    createTime = dbhandle.Column(dbhandle.DateTime, default=datetime.datetime.now())
    updateTime = dbhandle.Column(dbhandle.DateTime, default=datetime.datetime.now())

    def __repr__(self):
        return '<caseNo %r>' % self.caseNo