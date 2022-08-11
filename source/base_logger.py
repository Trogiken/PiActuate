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

debug_level = """\
[loggers]
keys=root,MainLogger

[handlers]
keys=consoleHandler

[formatters]
keys=consoleFormatter

[logger_root]
level=DEBUG
handlers=consoleHandler

[logger_MainLogger]
level=DEBUG
handlers=consoleHandler
qualname=MainLogger
propagate=0

[handler_consoleHandler]
class=StreamHandler
level=DEBUG
formatter=consoleFormatter
args=(sys.stdout,)

[formatter_consoleFormatter]
format=%(asctime)s | %(levelname)-8s | %(filename)-7s %(funcName)-10s %(lineno)04d | %(message)s
datefmt=%Y-%m-%d %H:%M:%S"""

info_level = """\
[loggers]
keys=root,MainLogger

[handlers]
keys=consoleHandler

[formatters]
keys=consoleFormatter

[logger_root]
level=INFO
handlers=consoleHandler

[logger_MainLogger]
level=INFO
handlers=consoleHandler
qualname=MainLogger
propagate=0

[handler_consoleHandler]
class=StreamHandler
level=INFO
formatter=consoleFormatter
args=(sys.stdout,)

[formatter_consoleFormatter]
format=%(asctime)s | %(levelname)-8s | %(filename)-7s %(funcName)-10s %(lineno)04d | %(message)s
datefmt=%Y-%m-%d %H:%M:%S"""

config = disk.Config()
home = disk.home
log_conf = os.path.join(home, 'source', 'logger_config.conf')
if config.load()['environment']['debug']:
    with open(log_conf, 'w') as f:
        f.write(debug_level)
else:
    with open(log_conf, 'w') as f:
        f.write(info_level)

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
