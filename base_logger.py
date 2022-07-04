import os
import logging.config
from datetime import datetime

logdir = "logs"
if not os.path.exists(logdir):
    os.mkdir(logdir)

logging.config.fileConfig('logger_config.conf')
log = logging.getLogger('MainLogger')

fh = logging.FileHandler('{}\\{:%Y-%m-%d}.log'.format(logdir, datetime.now()))
formatter = logging.Formatter('%(asctime)s | %(levelname)-8s | %(filename)s-%(funcName)s-%(lineno)04d | %(message)s', datefmt='%H:%M:%S')
fh.setFormatter(formatter)

log.addHandler(fh)
