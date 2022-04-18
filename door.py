import RPi.GPIO as GPIO
import time


# start = time.time()
# while time.time() < start + 5:  # Stops after at least 5 seconds

# GPIO.setup(0, GPIO.IN, pull_up_down=GPIO.PUD_UP) Change zero to what ever pin it's attached to

class Door:
    GPIO.setmode(GPIO.BCM)
    RELAY1 = 26
    RELAY2 = 20
    TOP_SWITCH = 0  # Change to correct pin
    BOTTOM_SWITCH = 0  # Change to correct pin
    GPIO.setup(RELAY1, GPIO.OUT, initial=0)
    GPIO.setup(RELAY2, GPIO.OUT, initial=0)

    def go(self, direction):
        directions = ['up', 'down']
        if direction in directions:
            if direction == 'up':
                RELAY = self.RELAY1
                SWITCH = self.TOP_SWITCH
            if direction == 'down':
                RELAY = self.RELAY2
                SWITCH = self.BOTTOM_SWITCH
        else:
            raise ValueError(f"Valid Directions: {directions}\n Direction Given: {direction}")

        start = time.time()
        exceeded_limit = True

        while time.time() < start + 5:  # Stops after at least 5 seconds
            if GPIO.input(SWITCH) is True:
                exceeded_limit = False
                break
            GPIO.output(RELAY, GPIO.HIGH)

        GPIO.output(RELAY, GPIO.LOW)
        if exceeded_limit:
            return False  # If door movement took longer than 5 seconds
        return True  # If door hit top switch with 5 seconds

    @staticmethod
    def status():
        pass
