from .base_logger import log
import RPi.GPIO as GPIO
import time


class Door:  # MAKE SURE PINS LOAD IN AS INTEGERS INSTEAD OF STRINGS
    def __init__(self, relay1, relay2, top_switch, bottom_switch, sensor, max_travel_time):
        GPIO.setmode(GPIO.BCM)
        self.RELAY1 = relay1
        self.RELAY2 = relay2
        self.TOP_SWITCH = top_switch  # Change to correct pin
        self.BOTTOM_SWITCH = bottom_switch  # Change to correct pin
        self.SENSOR = sensor  # Change to correct pin
        self.max_travel_time = max_travel_time
        GPIO.setup(self.RELAY1, GPIO.OUT, initial=True)
        GPIO.setup(self.RELAY2, GPIO.OUT, initial=True)
        GPIO.setup(self.TOP_SWITCH, GPIO.IN)
        GPIO.setup(self.BOTTOM_SWITCH, GPIO.IN)
        GPIO.setup(self.SENSOR, GPIO.IN)

        log.debug("GPIO: BCM")
        log.debug(f"Relay 1: {relay1}")
        log.debug(f"Relay 2: {relay2}")
        log.debug(f"Top Switch: {top_switch}")
        log.debug(f"Bottom Switch: {bottom_switch}")
        log.debug(f"Sensor: {sensor}")
        log.debug(f"Max Travel: {max_travel_time} seconds")

        self.in_motion = False

    def status(self):
        if GPIO.input(self.SENSOR):  # If sensor is blocked
            status = 'blocked'
        elif self.in_motion:  # If the door is moving
            status = 'moving'
        else:
            if GPIO.input(self.TOP_SWITCH) is True and GPIO.input(self.BOTTOM_SWITCH) is False:
                status = 'up'
            elif GPIO.input(self.TOP_SWITCH) is False and GPIO.input(self.BOTTOM_SWITCH) is True:
                status = 'down'
            else:
                status = 'unknown'

        return status

    def move(self, direction):
        exceeded_limit = True
        door_blocked = False
        already_at_position = False

        log.info("Movement Operation Startup...")
        log.debug(f"Requested Direction [{direction}]")

        if direction == 'up':
            if GPIO.input(self.TOP_SWITCH) is not True:  # If limit switch is not already triggered
                log.debug(f"Relay 2 ON: pin-{self.RELAY2}")
                GPIO.output(self.RELAY2, GPIO.LOW)
                log.info(f"In Motion [{direction}]")

                self.in_motion = True
                start = time.time()
                while time.time() < start + self.max_travel_time:  # Stops after at least max_travel_time
                    if GPIO.input(self.TOP_SWITCH) is True:  # If limit switch is triggered
                        exceeded_limit = False
                        break
                    else:
                        continue

                log.debug(f"Relay 2 OFF: pin-{self.RELAY2}")
                GPIO.output(self.RELAY2, GPIO.HIGH)
                log.info(f"Halted Motion [{direction}]")
                self.in_motion = False
            else:
                already_at_position = True
        elif direction == 'down':
            if GPIO.input(self.SENSOR) is not True:  # If not blocked
                if GPIO.input(self.BOTTOM_SWITCH) is not True:  # If limit switch is not already triggered
                    log.debug(f"Relay 1 ON: pin-{self.RELAY1}")
                    GPIO.output(self.RELAY1, GPIO.LOW)
                    log.info(f"In Motion [{direction}]")

                    self.in_motion = True
                    start = time.time()
                    while time.time() < start + self.max_travel_time:  # Stop least max_travel_time (Doesn't force stop)
                        if GPIO.input(self.BOTTOM_SWITCH) is True:  # If limit switch is triggered
                            exceeded_limit = False
                            break
                        elif GPIO.input(self.SENSOR) is True:
                            door_blocked = True
                            break
                        else:
                            continue

                    log.debug(f"Relay 1 OFF: pin-{self.RELAY1}")
                    GPIO.output(self.RELAY1, GPIO.HIGH)
                    log.info(f"Halted Motion [{direction}]")
                    self.in_motion = False
                else:
                    already_at_position = True
            else:
                door_blocked = True
        else:
            log.error("Invalid Direction")

        if door_blocked:
            self.move('up')
            log.warning("Door is Blocked")
        elif already_at_position:
            log.warning("Door already at requested position")
        elif exceeded_limit:  # If movement took longer than set seconds
            log.critical(f'Exceeded movement limit of {self.max_travel_time} seconds: [{direction}]')
        else:
            log.info(f'Door Moved Successfully: [{direction}]')  # If door hit limit switch within allowed time
