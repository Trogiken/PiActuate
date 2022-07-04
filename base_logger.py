import os
import logging.config
from datetime import datetime

if not os.path.exists("logs"):
    os.mkdir("logs")

logging.config.fileConfig('aaa.conf')
log = logging.getLogger('MainLogger')

fh = logging.FileHandler('logs\\{:%Y-%m-%d}.log'.format(datetime.now()))
formatter = logging.Formatter('%(asctime)s | %(levelname)-8s | %(filename)s-%(funcName)s-%(lineno)04d | %(message)s', datefmt='%H:%M:%S')
fh.setFormatter(formatter)

log.addHandler(fh)
