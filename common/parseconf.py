from configparser import ConfigParser

def parsedbcf(cfgdir):
    cfp = ConfigParser()
    cfp.read(cfgdir, encoding="utf-8-sig")
    host = cfp.get('mysql', 'host')
    username = cfp.get('mysql', 'username')
    password = cfp.get('mysql', 'password')
    dbname = cfp.get('mysql', 'dbname')
    port = cfp.get('mysql', 'port')
    return {"host": host, "username": username, "password": password, "dbname": dbname, "port": port}

def parsergtcf(cfgdir):
    cfp = ConfigParser()
    cfp.read(cfgdir, encoding="utf-8-sig")
    username = cfp.get('register', 'username')
    password = cfp.get('register', 'password')
    return username,password

def parseahcf(cfgdir):
    cfp = ConfigParser()
    cfp.read(cfgdir, encoding="utf-8-sig")
    app = cfp.get('auth', 'app')
    version = cfp.get('auth', 'version')
    srcret_key = cfp.get('auth', 'srcret_key')
    return app,version,srcret_key

def parsedvscf(cfgdir):
    cfp = ConfigParser()
    cfp.read(cfgdir, encoding="utf-8-sig")
    baseuri = cfp.get('baseuri', 'uri')
    deviceInfo = cfp.get('devices', 'dvs_uri')
    return baseuri,deviceInfo

def parsegtcrlcf(cfgdir):
    cfp = ConfigParser()
    cfp.read(cfgdir, encoding="utf-8-sig")
    baseuri = cfp.get('baseuri', 'uri')
    getTestcasesRunList = cfp.get('gtcrl', 'getTestcasesRunList_uri')
    getTestcasesRunList_uri = baseuri + getTestcasesRunList
    project_id = cfp.get('gtcrl', 'project_id')
    return getTestcasesRunList_uri,project_id

def parselgncf(cfgdir):
    cfp = ConfigParser()
    cfp.read(cfgdir, encoding="utf-8-sig")
    uri = cfp.get('baseuri', 'uri')
    lgn = cfp.get('login', 'lgn_uri')
    lgn_uri = uri + lgn
    username = cfp.get('login', 'username')
    password = cfp.get('login', 'password')
    return lgn_uri,username,password

def parseutttcf(cfgdir):
    cfp = ConfigParser()
    cfp.read(cfgdir, encoding="utf-8-sig")
    uri = cfp.get('baseuri', 'uri')
    thl = cfp.get('uttt', 'thl_uri')
    thl_uri = uri + thl
    return thl_uri

def parsepjt(cfgdir):
    cfp = ConfigParser()
    cfp.read(cfgdir, encoding="utf-8-sig")
    report_dir = cfp.get('project', 'report_dir')
    return report_dir

def parsedcecf(cfgdir):
    cfp = ConfigParser()
    cfp.read(cfgdir, encoding="utf-8-sig")
    cachedir = cfp.get('destroyCache', 'cachedir')
    return cachedir

def parseAppcf(cfgdir):
    cfp = ConfigParser()
    cfp.read(cfgdir, encoding="utf-8-sig")
    allureIP = cfp.get('app', 'allureIP')
    allurePort = cfp.get('app', 'allurePort')
    return allureIP,allurePort

# if __name__ == '__main__':
#     res = parsedbcf('../base.conf')
#     print(res)
