from datetime import datetime
import logging
import os

now = datetime.now()
log = logging
if not os.path.exists("logs"):
    os.mkdir("logs")
log.basicConfig(level=logging.INFO, filename=f"logs\\{now.strftime('%Y-%m-%d')}.log",
                format="%(asctime)s/%(levelname)s/%(filename)s[%(lineno)d]/%(message)s", datefmt="%H:%M:%S")
