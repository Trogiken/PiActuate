import os
import logging.config
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

path = Path(os.getcwd())
main_path = path.parents[0]
logdir = f"{main_path}\\logs"
if not os.path.exists(logdir):
    os.mkdir(logdir)

logging.config.fileConfig('logger_config.conf')
log = logging.getLogger('MainLogger')

fh = TimedRotatingFileHandler('{}\\chicken_door.log'.format(logdir), when='midnight', interval=1, backupCount=10)
fh.suffix = "%Y-%m-%d"
formatter = logging.Formatter('%(asctime)s | %(levelname)-8s | %(filename)s-%(funcName)s-%(lineno)04d | %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
fh.setFormatter(formatter)

log.addHandler(fh)
