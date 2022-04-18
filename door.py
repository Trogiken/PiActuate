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

    def open(self):
        start = time.time()

        while time.time() < start + 5:  # Stops after at least 5 seconds
            if GPIO.input(self.TOP_SWITCH) is True:
                GPIO.output(self.RELAY1, GPIO.LOW)
                return True  # If door hit top switch with 5 seconds
            GPIO.output(self.RELAY1, GPIO.HIGH)

        return False  # If door movement took longer than 5 seconds

    def close(self):
        GPIO.output(self.RELAY2, GPIO.HIGH)
        time.sleep(5)
        GPIO.output(self.RELAY2, GPIO.LOW)

    @staticmethod
    def status():
        pass
