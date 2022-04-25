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

    def status(self):
        top = GPIO.input(self.TOP_SWITCH)
        bottom = GPIO.input(self.BOTTOM_SWITCH)
        sensor = GPIO.input(self.LIGHT_SENSOR)

        status = {'position': None, 'path': None}

        if top and bottom is False or True:
            status['position'] = 'Incorrect'
        if top is True and bottom is False:
            status['position'] = 'Up'
        else:
            status['position'] = 'Down'
        if sensor is True:
            status['path'] = 'Blocked'
        else:
            status['path'] = 'Clear'

        return status

    def move(self, direction):  # TRY TO INCORPORATE STATUS FUNCTION FOR CHECKS
        directions = ['up', 'down']
        if direction in directions:
            if direction == 'up':
                relay = self.RELAY1
                switch = self.TOP_SWITCH
            elif direction == 'down':
                relay = self.RELAY2
                switch = self.BOTTOM_SWITCH
        else:
            return {'check': False, 'msg': 'Invalid Direction'}

        start = time.time()
        exceeded_limit = True

        if GPIO.input(self.LIGHT_SENSOR) is False:  # If light sensor isn't blocked
            GPIO.output(relay, GPIO.HIGH)
            while time.time() < start + self.max_travel_time:  # Stops after at least max_travel_time
                if GPIO.input(switch) is True:  # If limit switch is triggered
                    exceeded_limit = False
                    break
            GPIO.output(relay, GPIO.LOW)
        else:
            return {'check': False, 'msg': 'Sensor Blocked'}  # Light sensor is blocked

        if exceeded_limit:  # If movement took longer than set seconds
            return {'check': False, 'msg': f'Exceeded movement limit of {self.max_travel_time} seconds: [{direction}]'}
        return {'check': True, 'msg': f'Door Moved Successfully: [{direction}]'}  # If door hit switch within 5 seconds
