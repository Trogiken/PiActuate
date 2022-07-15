from .base_logger import log
import RPi.logger as GPIO
import time


class Door:
    def __init__(self, relay1, relay2, sw1, sw2, sw3, sw4, sw5, max_travel):
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        self.RELAY1 = relay1
        self.RELAY2 = relay2
        self.SW1 = sw1
        self.SW2 = sw2
        self.SW3 = sw3
        self.SW4 = sw4
        self.SW5 = sw5
        self.max_travel = max_travel
        self.status = None
        self.motion = 0

        log.debug(f"RELAY1: {self.RELAY1}")
        log.debug(f"RELAY2: {self.RELAY2}")
        log.debug(f"SW1: {self.SW1}")
        log.debug(f"SW2: {self.SW2}")
        log.debug(f"SW3: {self.SW3}")
        log.debug(f"SW4: {self.SW4}")
        log.debug(f"SW5: {self.SW5}")
        log.debug(f"max_travel: {self.max_travel}")

        GPIO.setup(self.RELAY1, GPIO.OUT, initial=True)
        GPIO.setup(self.RELAY2, GPIO.OUT, initial=True)
        GPIO.setup(self.SW1, GPIO.IN)
        GPIO.setup(self.SW2, GPIO.IN)
        GPIO.setup(self.SW3, GPIO.IN)
        GPIO.setup(self.SW4, GPIO.IN)
        GPIO.setup(self.SW5, GPIO.IN)

    def move(self, opt):
        log.info("[Operation Start]")

        if opt == 1:
            self.motion = 1
        elif opt == 2:
            self.motion = 2
        else:
            return

        start = time.time()
        while time.time() < start + self.max_travel:
            if GPIO.input(self.SW3) == 1:
                GPIO.output(self.RELAY1, True)
                GPIO.output(self.RELAY2, True)
                self.status = 'blocked'
            elif self.motion == 1 and GPIO.input(self.SW1) == 0 and GPIO.input(self.SW3) == 0:
                GPIO.output(self.RELAY1, False)
                GPIO.output(self.RELAY2, True)
                self.status = 'closing'
            elif self.motion == 2 and GPIO.input(self.SW2) == 0 and GPIO.input(self.SW3) == 0:
                GPIO.output(self.RELAY1, True)
                GPIO.output(self.RELAY2, False)
                self.status = 'opening'
            else:
                break
        self.motion = 0
        GPIO.output(self.RELAY1, True)
        GPIO.output(self.RELAY2, True)

        if GPIO.input(self.SW1) and not GPIO.input(self.SW2):
            self.status = 'closed'
        elif not GPIO.input(self.SW1) and GPIO.input(self.SW2):
            self.status = 'open'

        log.info(f'Door {self.status}')
        log.info("[Operation Stop]")
