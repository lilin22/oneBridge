import logging
import time
from logging.handlers import TimedRotatingFileHandler
from models import basePath

logDir = basePath + '\\logs\\'
now = time.strftime('%Y-%m-%d %H_%M_%S', time.localtime(time.time()))
logFileName=logDir+now+" "+".txt"

logger = logging.getLogger()
logger.setLevel(logging.INFO)

handler = TimedRotatingFileHandler(logFileName,
                                       "d",
                                       1,
                                       7,
                                       encoding="UTF-8")

formatter = logging.Formatter('[%(asctime)s] %(filename)s [%(funcName)s] [line:%(lineno)d] %(levelname)s:%(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)