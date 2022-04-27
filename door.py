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
        door_blocked = False
        already_at_position = False

        if direction == 'up':
            if GPIO.input(self.TOP_SWITCH) is not True:  # If limit switch is not already triggered
                GPIO.output(self.RELAY2, GPIO.HIGH)

                self.in_motion = True
                start = time.time()
                while time.time() < start + self.max_travel_time:  # Stops after at least max_travel_time
                    if GPIO.input(self.TOP_SWITCH) is True:  # If limit switch is triggered
                        exceeded_limit = False
                        break
                    else:
                        continue

                GPIO.output(self.RELAY2, GPIO.LOW)
                self.in_motion = False
            else:
                already_at_position = True
        elif direction == 'down':
            if GPIO.input(self.LIGHT_SENSOR) is not True:  # If not blocked
                if GPIO.input(self.BOTTOM_SWITCH) is not True:  # If limit switch is not already triggered
                    GPIO.output(self.RELAY1, GPIO.HIGH)

                    self.in_motion = True
                    start = time.time()
                    while time.time() < start + self.max_travel_time:  # Stop least max_travel_time (Doesn't force stop)
                        if GPIO.input(self.BOTTOM_SWITCH) is True:  # If limit switch is triggered
                            exceeded_limit = False
                            break
                        elif GPIO.input(self.LIGHT_SENSOR) is True:
                            door_blocked = True
                            break
                        else:
                            continue

                    GPIO.output(self.RELAY1, GPIO.LOW)
                    self.in_motion = False
                else:
                    already_at_position = True
            else:
                door_blocked = True
        else:
            return 'Invalid Direction'

        if door_blocked:
            self.move('up')
            return 'Door Blocked'
        elif already_at_position:
            return f'Door already: [{direction}]'
        elif exceeded_limit:  # If movement took longer than set seconds
            return f'Exceeded movement limit of {self.max_travel_time} seconds: [{direction}]'
        else:
            return f'Door Moved Successfully: [{direction}]'  # If door hit limit switch within 5 seconds
