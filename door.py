import RPi.GPIO as GPIO


class Door:
    RELAY1 = 26
    RELAY2 = 20
    RELAY3 = 21
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(RELAY1, GPIO.OUT, initial=0)
    GPIO.setup(RELAY2, GPIO.OUT, initial=0)
    GPIO.setup(RELAY3, GPIO.OUT, initial=0)
