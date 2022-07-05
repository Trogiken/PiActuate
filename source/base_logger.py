import os
import logging.config
from logging.handlers import TimedRotatingFileHandler

path = os.getcwd()
logdir = f"{path}\\logs"
if not os.path.exists(logdir):
    os.mkdir(logdir)

logging.config.fileConfig(f'{path}\\source\\logger_config.conf')
log = logging.getLogger('MainLogger')

fh = TimedRotatingFileHandler('{}\\chicken_door.log'.format(logdir), when='midnight', interval=1, backupCount=10)
fh.suffix = "%Y-%m-%d"

asc = "%(asctime)s"
levelname = "%(levelname)-8s"
filename = "%(filename)-8s"
funcname = "%(funcName)-10s"
linenum = "%(lineno)04d"
message = "%(message)s"
formatter = logging.Formatter(f'{asc} | {levelname} | {filename} {funcname} {linenum} | {message}', datefmt='%Y-%m-%d %H:%M:%S')
fh.setFormatter(formatter)

log.addHandler(fh)
