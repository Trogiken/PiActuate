import RPi.GPIO as GPIO
import time


class Door:  # MAKE SURE PINS LOAD IN AS INTEGERS INSTEAD OF STRINGS
    def __init__(self, relay1, relay2, top_switch, bottom_switch, light_sensor, max_travel_time):
        GPIO.setmode(GPIO.BCM)
        self.RELAY1 = relay1
        self.RELAY2 = relay2
        self.TOP_SWITCH = top_switch  # Change to correct pin
        self.BOTTOM_SWITCH = bottom_switch  # Change to correct pin
        self.LIGHT_SENSOR = light_sensor  # Change to correct pin
        self.max_travel_time = max_travel_time
        GPIO.setup(self.RELAY1, GPIO.OUT, initial=0)
        GPIO.setup(self.RELAY2, GPIO.OUT, initial=0)
        # GPIO.setup(0, GPIO.IN, pull_up_down=GPIO.PUD_UP) Change zero to what ever pin switch is attached to

        self.in_motion = False

    def status(self):
        top = GPIO.input(self.TOP_SWITCH)
        bottom = GPIO.input(self.BOTTOM_SWITCH)
        sensor = GPIO.input(self.LIGHT_SENSOR)

        if sensor is True:  # If sensor is blocked
            status = 'blocked'
        elif self.in_motion is True:  # If the door is moving
            status = 'moving'
        else:
            if top is True and bottom is False:
                status = 'up'
            elif top is False and bottom is True:
                status = 'down'
            else:
                status = 'unknown'

        return status

    def move(self, direction):
        exceeded_limit = True

        if direction == 'up':  # If light sensor isn't blocked
            if GPIO.input(self.TOP_SWITCH) is not True:  # If limit switch is not already triggered
                GPIO.output(self.RELAY2, GPIO.HIGH)

                self.in_motion = True
                start = time.time()
                while time.time() < start + self.max_travel_time:  # Stops after at least max_travel_time
                    if GPIO.input(self.TOP_SWITCH) is True:  # If limit switch is triggered
                        exceeded_limit = False
                        break

                GPIO.output(self.RELAY2, GPIO.LOW)
                self.in_motion = False
            else:
                return f'Door already {direction}'
        elif direction == 'down':
            if self.status() != 'blocked':
                if GPIO.input(self.BOTTOM_SWITCH) is not True:  # If limit switch is not already triggered
                    GPIO.output(self.RELAY1, GPIO.HIGH)

                    self.in_motion = True
                    door_blocked = False
                    start = time.time()
                    while time.time() < start + self.max_travel_time:  # Stops after at least max_travel_time
                        if GPIO.input(self.BOTTOM_SWITCH) is True:  # If limit switch is triggered
                            exceeded_limit = False
                            break
                        elif GPIO.input(self.LIGHT_SENSOR) is True:
                            door_blocked = True
                            break

                    GPIO.output(self.RELAY1, GPIO.LOW)
                    self.in_motion = False

                    if door_blocked is True:
                        self.move('up')
                        return 'Door Blocked'
                else:
                    return f'Door already {direction}'
        else:
            return 'Invalid Direction'

        if exceeded_limit:  # If movement took longer than set seconds
            return f'Exceeded movement limit of {self.max_travel_time} seconds: [{direction}]'
        return f'Door Moved Successfully: [{direction}]'  # If door hit switch within 5 seconds
