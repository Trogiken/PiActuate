from .base_logger import log
import RPi.GPIO as GPIO
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

    def get_status(self):
        if GPIO.input(self.SW1) == 1 and GPIO.input(self.SW2) == 0:
            self.status = 'closed'
        elif GPIO.input(self.SW1) == 0 and GPIO.input(self.SW2) == 1:
            self.status = 'open'
        elif GPIO.input(self.SW3) == 1:
            self.status = 'blocked'
        else:
            self.status = 'unknown'

        return self.status

    def move(self, opt):
        log.info("[Operation Start]")

        if opt == 1:
            self.motion = 1  # close
        elif opt == 2:
            self.motion = 2  # open
        else:
            log.error('Invalid Option')
            return
        log.debug(f"Motion = {self.motion}")

        time_exceeded = True
        blocked = False
        start = time.time()
        while time.time() < start + self.max_travel:  # Timer
            if self.motion == 1 and GPIO.input(self.SW1) == 0:
                if GPIO.input(self.SW3) == 1:
                    GPIO.output(self.RELAY1, True)
                    GPIO.output(self.RELAY2, True)
                    blocked = True
                else:
                    GPIO.output(self.RELAY1, False)
                    GPIO.output(self.RELAY2, True)
            elif self.motion == 2 and GPIO.input(self.SW2) == 0:
                GPIO.output(self.RELAY1, True)
                GPIO.output(self.RELAY2, False)
            else:
                time_exceeded = False
                blocked = False
                break
        self.motion = 0
        GPIO.output(self.RELAY1, True)
        GPIO.output(self.RELAY2, True)

        if time_exceeded:
            log.critical(f'Exceeded travel time of {self.max_travel} seconds')
        if blocked:
            log.warning("Door blocked; Opening Door")
            self.move(2)  # open door if blocked and timer exceeded
            return

        log.info(f"Status: {self.get_status()}")
        log.info("[Operation Stop]")
