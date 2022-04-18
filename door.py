import RPi.GPIO as GPIO
import time


class Door:
    GPIO.setmode(GPIO.BCM)
    RELAY1 = 26
    RELAY2 = 20
    TOP_SWITCH = 0  # Change to correct pin
    BOTTOM_SWITCH = 0  # Change to correct pin
    maximum_travel_time = 5
    GPIO.setup(RELAY1, GPIO.OUT, initial=0)
    GPIO.setup(RELAY2, GPIO.OUT, initial=0)
    # GPIO.setup(0, GPIO.IN, pull_up_down=GPIO.PUD_UP) Change zero to what ever pin switch is attached to

    def move(self, direction):
        directions = ['up', 'down']
        if direction == 'up':
            relay = self.RELAY1
            switch = self.TOP_SWITCH
        elif direction == 'down':
            relay = self.RELAY2
            switch = self.BOTTOM_SWITCH
        else:
            raise ValueError(f"Valid Directions: {directions}\nDirection Given: {direction}")

        start = time.time()
        exceeded_limit = True

        GPIO.output(relay, GPIO.HIGH)
        while time.time() < start + self.maximum_travel_time:  # Stops after at least 5 seconds
            if GPIO.input(switch) is True:  # If limit switch is triggered
                exceeded_limit = False
                break

        GPIO.output(relay, GPIO.LOW)
        if exceeded_limit:
            return False  # If door movement took longer than 5 seconds
        return True  # If door hit switch within 5 seconds

    def status(self):
        top = GPIO.input(self.TOP_SWITCH)
        bottom = GPIO.input(self.BOTTOM_SWITCH)

        if top and bottom is False or True:  # Incorrect Door Position
            if top is True and bottom is False:
                return 'up'
            elif top is False and bottom is True:
                return 'down'
        else:
            return False
