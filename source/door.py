from .base_logger import log
import RPi.GPIO as GPIO
import time
import threading

door_in_motion = False


class _Auxiliary(threading.Thread):
    def __init__(self, aux_sw3, aux_sw4, aux_sw5, relay1, relay2):
        super().__init__()
        self.AUX_SW1 = 23  # button 1
        self.AUX_SW2 = 24  # button 2
        self.AUX_SW3 = aux_sw3  # limit
        self.AUX_SW4 = aux_sw4  # limit
        self.AUX_SW5 = aux_sw5  # block
        self.RELAY1 = relay1
        self.RELAY2 = relay2
        self.motion = 0

        self.in_motion = False

        self._stop_event = threading.Event()

        GPIO.setup(self.AUX_SW1, GPIO.IN)
        GPIO.setup(self.AUX_SW2, GPIO.IN)

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()

    def run(self, *args, **kwargs):
        while True:
            if self.stopped():
                GPIO.output(self.RELAY1, True)
                GPIO.output(self.RELAY2, True)
                return
            if GPIO.input(self.AUX_SW1) == 1:
                self.motion = 1
                self.in_motion = True
            elif GPIO.input(self.AUX_SW2) == 1:
                self.motion = 2
                self.in_motion = True
            else:
                self.motion = 0

            if self.in_motion and not door_in_motion:
                if self.motion == 1 and GPIO.input(self.AUX_SW3) == 0:
                    self.in_motion = True
                    if GPIO.input(self.AUX_SW5) == 1:
                        GPIO.output(self.RELAY1, True)
                        GPIO.output(self.RELAY2, True)
                    else:
                        GPIO.output(self.RELAY1, False)
                        GPIO.output(self.RELAY2, True)
                elif self.motion == 2 and GPIO.input(self.AUX_SW4) == 0:
                    GPIO.output(self.RELAY1, True)
                    GPIO.output(self.RELAY2, False)
                else:
                    GPIO.output(self.RELAY1, True)
                    GPIO.output(self.RELAY2, True)
                    self.in_motion = False


class Door:
    """
    A class to control GPIO output and input of a door

    GPIO Mode: BCM

    ...

    Attributes
    ----------
    relay1 : int
        pin of channel 1 relay
    relay2 : int
        pin of channel 2 relay
    sw1 : int
        pin of limit switch
    sw2 : int
        pin of limit switch
    sw3 : int
        pint of block switch
    max_travel : int
        maximum seconds relays remain triggered

    Methods
    -------
    run_aux():
        start Auxiliary thread
    stop_aux():
        stop Auxiliary thread
    cleanup():
        resets relays and clears GPIO pins
    get_status():
        check if doors position is closed, open, blocked, or not known
    move(opt=int):
        move door open or closed
    """
    def __init__(self, relay1, relay2, sw1, sw2, sw3, max_travel):
        """
        Constructs all the necessary attributes for the Door object

        Parameters
        ----------
        relay1 : int
            pin of channel 1 relay
        relay2 : int
            pin of channel 2 relay
        sw1 : int
            pin of limit switch
        sw2 : int
            pin of limit switch
        sw3 : int
            pint of block switch
        max_travel : int
            maximum seconds relays remain triggered
        """
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        self.RELAY1 = relay1
        self.RELAY2 = relay2
        self.SW1 = sw1
        self.SW2 = sw2
        self.SW3 = sw3
        self.max_travel = max_travel

        self.status = None
        self.motion = 0
        self.in_motion = False
        self.aux = None
        self.is_running = False

        log.debug(f"RELAY1: {self.RELAY1}")
        log.debug(f"RELAY2: {self.RELAY2}")
        log.debug(f"SW1: {self.SW1}")
        log.debug(f"SW2: {self.SW2}")
        log.debug(f"SW3: {self.SW3}")
        log.debug(f"max_travel: {self.max_travel}")

        GPIO.setup(self.RELAY1, GPIO.OUT, initial=True)
        GPIO.setup(self.RELAY2, GPIO.OUT, initial=True)
        GPIO.setup(self.SW1, GPIO.IN)
        GPIO.setup(self.SW2, GPIO.IN)
        GPIO.setup(self.SW3, GPIO.IN)

    def run_aux(self):
        """Creates an Auxiliary object and starts the thread"""
        try:
            if self.is_running is False:
                self.aux = _Auxiliary(aux_sw3=self.SW1, aux_sw4=self.SW2, aux_sw5=self.SW3,
                                      relay1=self.RELAY1, relay2=self.RELAY2)
                self.aux.start()

                self.is_running = True
                log.info("Auxiliary is Running")
            else:
                log.warning("Auxiliary is already Running")
        except Exception:
            self.is_running = False
            log.exception("Auxiliary has failed to Run")

    def stop_aux(self):
        """Stops the Auxiliary thread and destroys the object"""
        try:
            if self.is_running is True:
                self.aux.stop()
                self.aux.join()

                self.aux = None
                self.is_running = False
                log.info("Auxiliary has stopped Running")
            else:
                log.warning("Auxiliary is not Running")
        except Exception:
            log.exception("Auxiliary has failed to Stop")

    def cleanup(self):
        """Resets relays and clears GPIO pins"""
        GPIO.output(self.RELAY1, True)
        GPIO.output(self.RELAY2, True)
        GPIO.cleanup()
        log.info("GPIO Cleared")

    def get_status(self):
        """
        Check door position

        Returns
        -------
        status (str): closed, open, blocked, or unknown
        """
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
        """
        Movement operation

        Relay outputs: True=Off, False=On

        Parameters
        ----------
        opt : int, required
            opt=1 (close), opt=2 (open)
        """
        log.info("[Operation Start]")

        if self.aux is not None:
            if self.aux.in_motion:  # If an auxiliary button is being pressed
                log.error("Auxiliary Active; Canceling Operation")
                return

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
        global door_in_motion
        start = time.time()
        while time.time() < start + self.max_travel:  # Timer
            door_in_motion = True
            if self.motion == 1 and GPIO.input(self.SW1) == 0:  # Requested down and limit switch not triggered
                if GPIO.input(self.SW3) == 1:  # Block switch triggered
                    GPIO.output(self.RELAY1, True)
                    GPIO.output(self.RELAY2, True)
                    blocked = True
                else:
                    GPIO.output(self.RELAY1, False)
                    GPIO.output(self.RELAY2, True)
            elif self.motion == 2 and GPIO.input(self.SW2) == 0:  # Requested up and limit switch not triggered
                GPIO.output(self.RELAY1, True)
                GPIO.output(self.RELAY2, False)
            else:  # Motion related limit switch is triggered
                time_exceeded = False
                blocked = False
                break
        # Reset motion and relays
        self.motion = 0
        GPIO.output(self.RELAY1, True)
        GPIO.output(self.RELAY2, True)
        door_in_motion = False

        if time_exceeded:
            log.critical(f'Exceeded travel time of {self.max_travel} seconds')
        if blocked:  # Open door if blocked=True and timer exceeded
            log.warning("Door blocked; Opening Door")
            self.move(2)
            return

        log.info(f"Status: {self.get_status()}")
        log.info("[Operation Stop]")
