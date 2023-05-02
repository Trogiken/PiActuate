from source.packages import timezone
from source.packages import SolarTime
from datetime import date, datetime, timedelta
from time import sleep
import threading
import re
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
        rise_offset = timedelta(minutes=self.sunrise_offset)
        set_offset = timedelta(minutes=self.sunset_offset)

        log.debug(f"Requested Date: {requested_date}")
        log.debug(f"Sunrise Offset: {self.sunrise_offset} minutes")
        log.debug(f"Sunset Offset: {self.sunset_offset} minutes")

        year = requested_date.year
        month = requested_date.month
        day = requested_date.day

        requested_date = date(year, month, day)
        localtz = timezone(self.zone)
        lat, lon = self.latitude, self.longitude

        sun = SolarTime()
        schedule_ = sun.sun_utc(requested_date, lat, lon)
        raw_sunset = schedule_['sunset'].astimezone(localtz)  # year-month-day hour:min:second-timezone
        raw_sunrise = schedule_['sunrise'].astimezone(localtz)  # year-month-day hour:min:second-timezone

        final_sunset = raw_sunset + set_offset
        final_sunrise = raw_sunrise + rise_offset
        pattern = r" (.*?)\-"

        sunset = re.search(pattern, str(final_sunset)).group(1)
        sunrise = re.search(pattern, str(final_sunrise)).group(1)

        # Remove seconds from time
        sunset = sunset[:len(sunset) - 3]
        sunrise = sunrise[:len(sunrise) - 3]

        return {'sunset': sunset, 'sunrise': sunrise}

    def run(self, *args, **kwargs):
        """Automation loop"""
        while True:
            today_date = date.today()
            tomorrow_date = date.today() + timedelta(days=1)
            today_suntimes = self.get_suntimes(today_date)
            tomorrow_suntimes = self.get_suntimes(tomorrow_date)

            request_refresh = False
            while True:
                if request_refresh:
                    log.debug("Refreshing...")
                    self._refresh_event.clear()
                    break
                
                current_date = date.today()
                current_time = datetime.now(timezone(self.zone)).strftime("%H:%M")
                current_status = self.door.get_status()
                self.active_current = current_time

                log.debug(f"Current Date: {current_date}")
                log.debug(f"Current Time: {current_time}")
                log.debug(f"Current Status: {current_status}")

                if current_date == today_date:
                    sunrise = today_suntimes['sunrise']
                    sunset = today_suntimes['sunset']
                elif current_date == tomorrow_date:
                    sunrise = tomorrow_suntimes['sunrise']
                    sunset = today_suntimes['sunset']
                else:
                    log.warning("Date comparison failed, refreshing data...")
                    break

                self.active_sunrise = sunrise
                self.active_sunset = sunset
                log.debug(f"Sunset set to [{sunset}]")
                log.debug(f"Sunrise set to [{sunrise}]")

                if sunrise <= current_time < sunset:
                    if current_status == 'closed':
                        log.info("Door Called Up")
                        self.door.move(2)
                        sleep(1)
                        break
                else:
                    if current_status == 'open':
                        log.info("Door Called Down")
                        self.door.move(1)
                        sleep(1)
                        break
                i = 0
                while i != 60:  # Wait for some seconds, checking for stop event each second
                    i += 1
                    if self._stop_event.is_set():
                        log.debug("Stopping...")
                        return
                    if self._refresh_event.is_set():
                        request_refresh = True
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

    Methods
    -------
    run():
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

        self.sch = _Scheduler(door=self.door, zone=self.zone, longitude=self.longitude, latitude=self.latitude,
                              sunset_offset=self.sunset_offset, sunrise_offset=self.sunrise_offset)  # init variable

        self.is_running = False  # can be used externally to check scheduler thread status

    def run(self):
        """Creates a scheduler object and starts the thread"""
        try:
            if not self.sch.is_alive():
                self.sch = _Scheduler(door=self.door, zone=self.zone, longitude=self.longitude, latitude=self.latitude,
                                      sunset_offset=self.sunset_offset, sunrise_offset=self.sunrise_offset)
                self.sch.start()
                self.is_running = True
                log.info("Scheduler is Running")
            else:
                log.warning("Scheduler is already Running")
        except Exception:
            self.is_running = False
            log.exception("Scheduler has failed to Run")

    def stop(self):
        """Stops the scheduler thread"""
        try:
            if self.sch.is_alive():
                self.sch.stop()
                self.sch.join()

                self.is_running = False
                log.info("Scheduler has stopped Running")
            else:
                log.warning("Scheduler is not Running")
        except Exception:
            log.exception("Scheduler has failed to Stop")

    def set_sunrise_offset(self, value):
        """Changes Auto() and _Scheduler() attribute "sunrise_offset" to (value)"""
        self.sunrise_offset = value
        if self.sch.is_alive():
            self.sch.sunrise_offset = value

    def set_sunset_offset(self, value):
        """Changes Auto() and _Scheduler() attribute "sunset_offset" to (value)"""
        self.sunset_offset = value
        if self.sch.is_alive():
            self.sch.sunset_offset = value

    def refresh(self):
        """Calls scheduler thread event 'refresh()'"""
        if self.sch.is_alive():
            self.sch.refresh()

    def active_sunrise(self):
        """
        Get sunrise time from scheduler

        Returns:
        -------
        sch.active_sunrise (str): 00:00 string format
        """
        if self.sch.is_alive():
            return self.sch.active_sunrise
        else:
            return None

    def active_sunset(self):
        """
        Get sunset time from scheduler

        Returns:
        -------
        sch.active_sunset (str): 00:00 string format
        """
        if self.sch.is_alive():
            return self.sch.active_sunset
        else:
            return None
    
    def active_current(self):
        """
        Get current time from scheduler

        Returns:
        -------
        sch.active_current (str): 00:00 string format
        """
        if self.sch.is_alive():
            return self.sch.active_current
        else:
            return None
