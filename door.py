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
        directions = ['up', 'down']
        if direction in directions:
            if direction == 'up':
                relay = self.RELAY1
                switch = self.TOP_SWITCH
            elif direction == 'down':
                relay = self.RELAY2
                switch = self.BOTTOM_SWITCH
            else:
                raise ValueError('Direction was not detected as up nor down')
        else:
            return 'Invalid Direction'

        status = self.status()
        exceeded_limit = True

        if status == 'blocked':  # If light sensor isn't blocked
            if GPIO.input(switch) is not True:  # If limit switch is not already triggered
                GPIO.output(relay, GPIO.HIGH)
                self.in_motion = True
                start = time.time()
                while time.time() < start + self.max_travel_time:  # Stops after at least max_travel_time
                    if GPIO.input(switch) is True:  # If limit switch is triggered
                        exceeded_limit = False
                        break
                GPIO.output(relay, GPIO.LOW)
                self.in_motion = False
            else:
                return f'Door already {direction}'
        else:
            return 'Sensor Blocked'  # Light sensor is blocked

        if exceeded_limit:  # If movement took longer than set seconds
            return f'Exceeded movement limit of {self.max_travel_time} seconds: [{direction}]'
        return f'Door Moved Successfully: [{direction}]'  # If door hit switch within 5 seconds
