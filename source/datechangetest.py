from base_logger import log
from time import sleep

num = 1
while True:
    log.critical(f"Change Test - {num}")
    num += 1
    sleep(10)
