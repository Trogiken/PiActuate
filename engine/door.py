import time
import threading
import logging

log = logging.getLogger('root')

try:
    import RPi.GPIO as GPIO
except (ImportError, ModuleNotFoundError):
    log.exception("Failed to import RPi.GPIO")
    raise

class Auxiliary(threading.Thread):
    def __init__(self, aux_sw1, aux_sw2, aux_sw3, aux_sw4, aux_sw5, off_state, relay1, relay2):
        super().__init__()
        self.AUX_SW1 = aux_sw1  # trigger relay1
        self.AUX_SW2 = aux_sw2  # trigger relay2
        self.AUX_SW3 = aux_sw3  # limit
        self.AUX_SW4 = aux_sw4  # limit
        self.AUX_SW5 = aux_sw5  # block
        self.OFF_STATE = off_state
        self.RELAY1 = relay1
        self.RELAY2 = relay2

        self.motion = 0
        self.in_motion = False
        self._stop_event = threading.Event()
        self._pause_event = threading.Event()

        log.info("AUX pins setting up...")
        try:
            GPIO.setup(self.AUX_SW1, GPIO.IN)
            GPIO.setup(self.AUX_SW2, GPIO.IN)
        except Exception:
            log.exception("Failed to set up AUX pins")
            raise

        log.info("Aux pins set up successfully")

    def pause(self):
        log.debug("Auxiliary Paused")
        self._pause_event.set()
    
    def paused(self):
        return self._pause_event.is_set()

    def resume(self):
        log.debug("Auxiliary Resumed")
        self._pause_event.clear()

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()

    def run(self, *args, **kwargs):
        while not self.stopped():
            while self.paused():
                time.sleep(0.1)

            if GPIO.input(self.AUX_SW1) == 1:
                self.motion = 1
                self.in_motion = True
            elif GPIO.input(self.AUX_SW2) == 1:
                self.motion = 2
                self.in_motion = True
            else:
                self.motion = 0

            if self.in_motion:
                if self.motion == 1 and GPIO.input(self.AUX_SW3) == 0:
                    self.in_motion = True
                    if GPIO.input(self.AUX_SW5) == 1:
                        self._trigger_relays(self.OFF_STATE, self.OFF_STATE)
                    else:
                        self._trigger_relays(not self.OFF_STATE, self.OFF_STATE)
                elif self.motion == 2 and GPIO.input(self.AUX_SW4) == 0:
                    self._trigger_relays(self.OFF_STATE, not self.OFF_STATE)
                else:
                    self._trigger_relays(self.OFF_STATE, self.OFF_STATE)
                    self.in_motion = False

    def _trigger_relays(self, relay1_state, relay2_state):
        GPIO.output(self.RELAY1, relay1_state)
        GPIO.output(self.RELAY2, relay2_state)

class Door:
    """
    A class to control GPIO output and input of a door

    GPIO Mode: BCM

    ...

    Attributes
    ----------
    OFF_STATE: bool
        Send power to turn relays off or not
    RELAY2 : int
        pin of channel 1 relay
    RELAY2 : int
        pin of channel 2 relay
    SW1 : int
        pin of limit switch
    SW2 : int
        pin of limit switch
    SW3 : int
        pin of block switch
    SW4 : int
        pin of aux_switch1
    SW5 : int
        pint of aux_switch2
    travel_time : int
        maximum seconds relays remain triggered
    auxiliary: object
        auxiliary thread object

    Methods
    -------
    run_aux():
        start Auxiliary thread
    stop_aux():
        stop Auxiliary thread
    cleanup():
        resets relays and clears GPIO pins
    status():
        check if doors position is closed, open, blocked, or not known
    move(opt=int):
        move door open or closed
    """
    def __init__(self, board_mode: str, off_state: bool, relay1: int, relay2: int, sw1: int, sw2: int, sw3: int, sw4: int, sw5: int, travel_time: int):
        """Constructs all the necessary attributes for the Door object"""
        if board_mode.casefold() == 'bcm':
            GPIO.setmode(GPIO.BCM)
            log.debug("GPIO mode set to BCM")
        elif board_mode.casefold() == 'board':
            GPIO.setmode(GPIO.BOARD)
            log.debug("GPIO mode set to BOARD")
        else:
            log.error('Invalid GPIO board mode')
            raise IOError

        GPIO.setwarnings(False)
        self.OFF_STATE = off_state
        self.RELAY1 = relay1
        self.RELAY2 = relay2
        self.SW1 = sw1
        self.SW2 = sw2
        self.SW3 = sw3
        self.SW4 = sw4
        self.SW5 = sw5
        self.travel_time = travel_time

        self.motion = 0
        self.auxiliary = threading.Thread()
        self._move_op_thread = threading.Thread()

        log.debug(f"off_state: {self.OFF_STATE}")
        log.debug(f"RELAY1: {self.RELAY1}")
        log.debug(f"RELAY2: {self.RELAY2}")
        log.debug(f"SW1: {self.SW1}")
        log.debug(f"SW2: {self.SW2}")
        log.debug(f"SW3: {self.SW3}")
        log.debug(f"SW4: {self.SW4}")
        log.debug(f"SW5: {self.SW5}")
        log.debug(f"max_travel: {self.travel_time}")

        log.info("Main pins setting up...")
        try:
            GPIO.setup(self.RELAY1, GPIO.OUT, initial=self.OFF_STATE)
            GPIO.setup(self.RELAY2, GPIO.OUT, initial=self.OFF_STATE)
            GPIO.setup(self.SW1, GPIO.IN)
            GPIO.setup(self.SW2, GPIO.IN)
            GPIO.setup(self.SW3, GPIO.IN)
        except Exception:
            log.exception("Failed to setup main pins")
            raise IOError
        
        log.info("Main pins setup successfully")

    def run_aux(self):
        """Creates an Auxiliary object and starts the thread"""
        try:
            if not self.auxiliary.is_alive():
                self.auxiliary = Auxiliary(aux_sw1=self.SW4, aux_sw2=self.SW5, aux_sw3=self.SW1, aux_sw4=self.SW2,
                                     aux_sw5=self.SW3, off_state=self.OFF_STATE, relay1=self.RELAY1, relay2=self.RELAY2)
                self.auxiliary.start()
                log.info("Auxiliary is Running")
            else:
                log.warning("Auxiliary is already Running")
        except Exception:
            log.exception("Auxiliary has failed to Run")

    def stop_aux(self):
        """Stops the Auxiliary thread and destroys the object"""
        try:
            if self.auxiliary.is_alive():
                self.auxiliary.stop()
                self.auxiliary.join()
                log.info("Auxiliary has stopped Running")
            else:
                log.warning("Auxiliary is not Running")
        except Exception:
            log.exception("Auxiliary has failed to Stop")

    def cleanup(self):
        """Resets relays and clears GPIO pins"""
        self.stop_aux()
        if self._move_op_thread.is_alive():
            self._move_op_thread.join()  # wait for thread to complete
        GPIO.output(self.RELAY1, self.OFF_STATE)
        GPIO.output(self.RELAY2, self.OFF_STATE)
        GPIO.cleanup()
        log.info("GPIO Cleared")

    @property
    def status(self):
        """
        Check door position

        Returns
        -------
        status (str): Closed, Open, Blocked, Extending, Retracting or Unknown
        """
        sw1_state = GPIO.input(self.SW1)
        sw2_state = GPIO.input(self.SW2)
        sw3_state = GPIO.input(self.SW3)

        if sw1_state == 1 and sw2_state == 0:
            status = 'Closed'
        elif sw1_state == 0 and sw2_state == 1:
            status = 'Open'
        elif sw3_state == 1:
            status = 'Blocked'
        elif self._move_op_thread.is_alive() or (self.auxiliary.is_alive() and self.auxiliary.in_motion):
            if self.motion == 1 or (self.auxiliary.is_alive() and self.auxiliary.motion == 1):
                status = 'Extending'
            elif self.motion == 2 or (self.auxiliary.is_alive() and self.auxiliary.motion == 2):
                status = 'Retracting'
            else:
                status = 'Unknown'
        else:
            status = 'Unknown'

        return status

    def _move_op(self, opt):
        """
        Movement operation

        Relay outputs: True=Off, False=On

        Parameters
        ----------
        opt : int, required
            opt=1 (close), opt=2 (open)
        """
        log.info("[Operation Start]")

        if self.auxiliary.is_alive() and self.auxiliary.in_motion:
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
        self.auxiliary.pause()  # pause auxiliary thread to prevent interference while moving

        time_exceeded = True
        blocked = False
        start = time.time()
        while time.time() < start + self.travel_time:  # Timer
            if self.motion == 1 and GPIO.input(self.SW1) == 0:  # Requested down and limit switch not triggered
                if GPIO.input(self.SW3) == 1:  # Block switch triggered
                    GPIO.output(self.RELAY1, self.OFF_STATE)
                    GPIO.output(self.RELAY2, self.OFF_STATE)
                    blocked = True
                else:
                    GPIO.output(self.RELAY1, not self.OFF_STATE)
                    GPIO.output(self.RELAY2, self.OFF_STATE)
            elif self.motion == 2 and GPIO.input(self.SW2) == 0:  # Requested up and limit switch not triggered
                GPIO.output(self.RELAY1, self.OFF_STATE)
                GPIO.output(self.RELAY2, not self.OFF_STATE)
            else:  # Motion-related limit switch is triggered
                time_exceeded = False
                blocked = False
                break

        # Reset motion and relays
        self.motion = 0
        self.auxiliary.resume()
        GPIO.output(self.RELAY1, self.OFF_STATE)
        GPIO.output(self.RELAY2, self.OFF_STATE)

        if time_exceeded:
            log.warning(f'Exceeded travel time of {self.travel_time} seconds')
        if blocked:  # Open door if blocked=True and timer exceeded
            log.warning("Door blocked; Opening Door")
            self._move_op(2)

        log.info(f"Status: {self.status}")
        log.info("[Operation Stop]")

    def move(self, opt):
        """Creates _move_op thread if there isn't one"""
        if not self._move_op_thread.is_alive():
            self._move_op_thread = threading.Thread(target=self._move_op, args=(opt,))
            self._move_op_thread.start()
            log.info("Movement thread started")
        else:
            log.info("Door already in motion")