"""
***Logger used throughout program***
Creates "logs" directory at top of directory
Current day log name "chicken_door.log"
Every midnight the current log name gets a suffix
"""
import os
import logging.config
from . import disk  # DEBUG: from . import disk
from logging.handlers import TimedRotatingFileHandler

config = disk.Config()
data = config.load()
lg = data['logging']
formatting = data['logging']['formatting']

debug_level = f"""\
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
format={formatting['format']}
datefmt={formatting['date']}"""

info_level = f"""\
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
format={formatting['format']}
datefmt={formatting['date']}"""

home = disk.home
config_name = 'logger_config.conf'

config_path = os.path.join(home, 'source', config_name)
with open(config_path, 'w') as f:
    if lg['debug']:
        f.write(debug_level)
    else:
        f.write(info_level)

logdir = os.path.join(home, 'logs')
if not os.path.exists(logdir):
    os.mkdir(logdir)

logging.config.fileConfig(config_path)
log = logging.getLogger('MainLogger')

fh = TimedRotatingFileHandler(os.path.join(logdir, lg['filename']), when='midnight', interval=1, backupCount=lg['backups'])
fh.suffix = lg['suffix']

formatter = logging.Formatter(formatting['format'], datefmt=formatting['date'])
fh.setFormatter(formatter)

log.addHandler(fh)
