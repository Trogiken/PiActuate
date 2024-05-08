from datetime import date, datetime, timedelta
from solartime import SolarTime
from pytz import timezone
from time import sleep
import threading
import logging

log = logging.getLogger('root')


class _Scheduler(threading.Thread):
    def __init__(self, door, zone, longitude, latitude, sunrise_offset, sunset_offset):
        super().__init__()
        self.longitude = longitude
        self.latitude = latitude
        self.sunrise_offset = sunrise_offset
        self.sunset_offset = sunset_offset
        self.zone = zone
        self.door = door

        self.active_sunrise = None
        self.active_sunset = None
        self.active_current = None

        self._refresh_event = threading.Event()
        self._stop_event = threading.Event()

    def refresh(self):
        self._refresh_event.set()

    def stop(self):
        self._stop_event.set()

    def get_suntimes(self, requested_date):
        """Gets sunrise and sunset times (HH:MM) for requested date"""
        year, month, day = requested_date.year, requested_date.month, requested_date.day

        try:
            schedule = SolarTime().sun_utc(date(year, month, day), self.latitude, self.longitude)
            localtz = timezone(self.zone)
            sunrise = (schedule['sunrise'].astimezone(localtz) + timedelta(minutes=self.sunrise_offset)).strftime("%H:%M")
            sunset = (schedule['sunset'].astimezone(localtz) + timedelta(minutes=self.sunset_offset)).strftime("%H:%M")
            log.debug(f"Requested Date: {requested_date}, Sunrise Offset: {self.sunrise_offset}, Sunset Offset: {self.sunset_offset}")
            log.debug(f"Sunrise: {sunrise}, Sunset: {sunset}")
            return {'sunset': sunset, 'sunrise': sunrise}
        except Exception as e:
            raise Exception(f"An error occurred when figuring sun times: {e}")
    
    def get_active_times(self):
        """Compares current time to sunrise and sunset times and returns active times accordingly"""
        today_date = datetime.now(timezone(self.zone)).date()
        tomorrow_date = today_date + timedelta(days=1)
        try:
            today_suntimes = self.get_suntimes(today_date)
            tomorrow_suntimes = self.get_suntimes(tomorrow_date)
        except Exception:
            log.exception("Problem getting sun times")
            

        # set the times that will be compared
        current_time = datetime.now(timezone(self.zone)).strftime("%H:%M")
        if current_time >= today_suntimes['sunset']:
            active_sunrise = tomorrow_suntimes['sunrise']
            active_sunset = tomorrow_suntimes['sunset']
        elif current_time < today_suntimes['sunset']:
            active_sunrise = today_suntimes['sunrise']
            active_sunset = today_suntimes['sunset']
        else:
            raise Exception(f"Something went wrong setting up active times: Current Time: {current_time}, Today Sun Times: {today_suntimes}, Tommorrow Sun Times: {tomorrow_suntimes}")
        
        return current_time, active_sunrise, active_sunset

    def run(self, *args, **kwargs):
        """Automation loop"""
        while not self._stop_event.is_set():
            try:
                self.active_current, self.active_sunrise, self.active_sunset = self.get_active_times()
            except Exception:
                log.exception("Problem getting active times, stopping scheduler")
                self._stop_event.set()
                continue  # skip the rest of the loop
                

            # Compare rise and set to the current time
            # Check if the door is open or closed, if it is open, close it, if it is closed, open it
            if self.active_sunrise <= self.active_current < self.active_sunset:
                log.debug(f'Door open conditions met: Current Time: {self.active_current}')
                if self.door.status == 'Closed':
                    log.info("Opening Door")
                    self.door.move(2)
                else:
                    log.debug(f"Did Not Open Door! | Door Status: {self.door.status}")
            elif self.active_current < self.active_sunrise or self.active_current >= self.active_sunset:
                log.debug(f'Door close conditions met: Current Time: {self.active_current}')
                if self.door.status == 'Open':
                    log.info("Closing Door")
                    self.door.move(1)
                else:
                    log.debug(f"Did Not Close Door! | Door Status: {self.door.status}")
            else:
                log.error("Something went wrong comparing times")


            i = 0   # counter
            while i != 60:
                i += 1
                if self._stop_event.is_set():
                    log.debug("Stopping...")
                    return
                if self._refresh_event.is_set(): # skip count down
                    log.debug("Refreshing...")
                    self._refresh_event.clear()
                    break
                sleep(1)


class Auto:
    """
    A class to open and close relays autonomously

    ...

    Attributes
    ----------
    door : object
        door class object
    zone : str
        time zone
    longitude : float
        longitudinal coordinate
    latitude : float
        latitudinal coordinate
    sunrise_offset : int
        add or sub minutes from time
    sunset_offset : int
        add or sub minutes from time
    scheduler : object
        scheduler thread object

    Methods
    -------
    start():
        start the scheduler thread
    stop():
        stop the scheduler thread
    set_sunrise_offset():
        set sunrise offset time (HH:MM) Call refresh() to apply changes
    set_sunset_offset():
        set sunset offset time (HH:MM) Call refresh() to apply changes
    refresh():
        refresh dates and times
    active_sunrise():
        get sunrise time from scheduler
    active_sunset():
        get sunset time from scheduler
    active_current():
        get current time from scheduler
    """
    def __init__(self, door, zone, longitude, latitude, sunrise_offset, sunset_offset):
        """Constructs all necessary attributes for the Auto object"""
        self.longitude = longitude
        self.latitude = latitude
        self.sunrise_offset = sunrise_offset
        self.sunset_offset = sunset_offset
        self.zone = zone
        self.door = door

        self.scheduler = threading.Thread()

    def start(self):
        """Creates a scheduler object and starts the thread"""
        try:
            if not self.scheduler.is_alive():
                self.scheduler = _Scheduler(door=self.door, zone=self.zone, longitude=self.longitude, latitude=self.latitude,
                                      sunset_offset=self.sunset_offset, sunrise_offset=self.sunrise_offset)
                self.scheduler.start()
                log.info("Scheduler is Running")
            else:
                log.info("Scheduler is already Running")
        except Exception:
            log.exception("Scheduler has failed to Run")

    def stop(self):
        """Stops the scheduler thread"""
        try:
            if self.scheduler.is_alive():
                self.scheduler.stop()
                self.scheduler.join()
                log.info("Scheduler has stopped Running")
            else:
                log.info("Scheduler is not Running")
        except Exception:
            log.exception("Scheduler has failed to Stop")

    def set_sunrise_offset(self, value):
        """Changes Auto() and _Scheduler() attribute "sunrise_offset" to (value)"""
        self.sunrise_offset = value
        if self.scheduler.is_alive():
            self.scheduler.sunrise_offset = value

    def set_sunset_offset(self, value):
        """Changes Auto() and _Scheduler() attribute "sunset_offset" to (value)"""
        self.sunset_offset = value
        if self.scheduler.is_alive():
            self.scheduler.sunset_offset = value

    def refresh(self):
        """Calls scheduler thread event 'refresh()'"""
        if self.scheduler.is_alive():
            self.scheduler.refresh()

    def active_sunrise(self):
        """
        Get sunrise time from scheduler

        Returns:
        -------
        scheduler.active_sunrise (str): 00:00 string format
        """
        if self.scheduler.is_alive():
            return self.scheduler.active_sunrise
        else:
            return None

    def active_sunset(self):
        """
        Get sunset time from scheduler

        Returns:
        -------
        scheduler.active_sunset (str): 00:00 string format
        """
        if self.scheduler.is_alive():
            return self.scheduler.active_sunset
        else:
            return None
    
    def active_current(self):
        """
        Get current time from scheduler

        Returns:
        -------
        scheduler.active_current (str): 00:00 string format
        """
        if self.scheduler.is_alive():
            return self.scheduler.active_current
        else:
            return None
