"""
***Logger used throughout program***
Creates "logs" directory at top of directory
Current day log name "chicken_door.log"
Every midnight the current log name gets a suffix (year-month-day)
"""
import os
import logging.config
import disk
from logging.handlers import TimedRotatingFileHandler

home = disk.home

logdir = os.path.join(home, 'logs')
if not os.path.exists(logdir):
    os.mkdir(logdir)

logging.config.fileConfig((os.path.join(home, 'source', 'logger_config.conf')))
log = logging.getLogger('MainLogger')

fh = TimedRotatingFileHandler(os.path.join(logdir, 'chicken_door.log'), when='midnight', interval=1, backupCount=10)
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
