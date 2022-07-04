import os
import logging.config
from pathlib import Path
from datetime import datetime

path = Path(os.getcwd())
main_path = path.parents[0]
logdir = f"{main_path}\\logs"
if not os.path.exists(logdir):
    os.mkdir(logdir)

logging.config.fileConfig('logger_config.conf')
log = logging.getLogger('MainLogger')

fh = logging.FileHandler('{}\\{:%Y-%m-%d}.log'.format(logdir, datetime.now()))
formatter = logging.Formatter('%(asctime)s | %(levelname)-8s | %(filename)s-%(funcName)s-%(lineno)04d | %(message)s', datefmt='%H:%M:%S')
fh.setFormatter(formatter)

log.addHandler(fh)
