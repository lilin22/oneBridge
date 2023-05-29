import pymysql

#数据库连接
def sqlConnect(host,username,passwd,db,port,use_unicode=True,charset="utf8"):
    conn = pymysql.connect(host=host, user=username, password=passwd, database=db, port=int(port),
                           use_unicode=use_unicode, charset=charset)
    return conn

#创建表
def createTbe(conn,sql):
    csr = conn.cursor()
    csr.execute(sql)
    csr.execute(sql)

#sql查询一行
def select(conn,sql):
    csr = conn.cursor()
    csr.execute(sql)
    data = csr.fetchone()
    conn.commit()
    return data

#sql查询所有行
def selectAll(conn,sql):
    csr = conn.cursor()
    csr.execute(sql)
    data = csr.fetchall()
    return data

#sql插入
def insert(conn,sql):
    csr = conn.cursor()
    try:
        csr.execute(sql)
        conn.commit()
    except:
        conn.rollback()

#sql更新
def update(conn,sql):
    csr = conn.cursor()
    try:
        csr.execute(sql)
        conn.commit()
    except:
        conn.rollback()

#sql删除
def delete(conn,sql):
    csr = conn.cursor()
    try:
        csr.execute(sql)
        conn.commit()
    except:
        conn.rollback()

#清空表数据
def truncate(conn,sql):
    csr = conn.cursor()
    try:
        csr.execute(sql)
        conn.commit()
    except:
        conn.rollback()

#关闭数据库
def sqlcls(conn):
    conn.close()
