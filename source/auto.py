from datetime import date, datetime, timedelta
from pytz import timezone
from solartime import SolarTime
from time import sleep
from .base_logger import log
import threading
import re


class Scheduler(threading.Thread):
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

        self._stop_event = threading.Event()

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()

    def get_world(self):
        today = datetime.today()
        rise_offset = timedelta(minutes=self.sunrise_offset)
        set_offset = timedelta(minutes=self.sunset_offset)

        log.debug(f"Sunrise Offset: {self.sunrise_offset} minutes")
        log.debug(f"Sunset Offset: {self.sunset_offset} minutes")

        year = today.year
        month = today.month
        day = today.day

        today = date(year, month, day)
        localtz = timezone(self.zone)
        lat, lon = self.latitude, self.longitude

        sun = SolarTime()
        schedule_ = sun.sun_utc(today, lat, lon)
        raw_sunset = schedule_['sunset'].astimezone(localtz)  # year-month-day hour:min:second-timezone
        raw_sunrise = schedule_['sunrise'].astimezone(localtz)  # year-month-day hour:min:second-timezone

        final_sunset = raw_sunset + set_offset
        final_sunrise = raw_sunrise + rise_offset
        pattern = r" (.*?)\-"

        sunset = re.search(pattern, str(final_sunset)).group(1)
        sunrise = re.search(pattern, str(final_sunrise)).group(1)

        return {'today': str(today), 'sunset': sunset, 'sunrise': sunrise}

    def run(self, *args, **kwargs):
        cycle = 1
        while True:
            log.info(f"Cycle: {cycle}")

            sun_data = self.get_world()
            sunrise = sun_data['sunrise']
            sunset = sun_data['sunset']

            sunrise = sunrise[:len(sunrise) - 3]
            sunset = sunset[:len(sunset) - 3]

            self.active_sunrise = sunrise
            self.active_sunset = sunset

            log.info(f"Sunset set to [{sunset}]")
            log.info(f"Sunrise set to [{sunrise}]")

            while True:
                current = datetime.now().strftime("%H:%M")
                status = self.door.get_status()

                if sunrise <= current < sunset:
                    if status == 'closed':
                        log.info("Door Called Up")
                        self.door.move(2)
                        break
                else:
                    if status == 'open':
                        log.info("Door Called Down")
                        self.door.move(1)
                        break
                i = 0
                while i != 60:  # Wait for some seconds, checking for stop event each second
                    i += 1
                    if self.stopped():
                        return
                    sleep(1)
            cycle += 1


class Auto:
    def __init__(self, door, zone, longitude, latitude, sunrise_offset, sunset_offset):
        self.longitude = longitude
        self.latitude = latitude
        self.sunrise_offset = sunrise_offset
        self.sunset_offset = sunset_offset
        self.zone = zone
        self.door = door

        self.sch = None

        self.is_running = False

    def run(self):
        try:
            if self.is_running is False:
                self.sch = Scheduler(door=self.door, zone=self.zone, longitude=self.longitude, latitude=self.latitude,
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
        try:
            if self.is_running is True:
                self.sch.stop()
                self.sch.join()

                self.sch = None
                self.is_running = False
                log.info("Scheduler has stopped Running")
            else:
                log.warning("Scheduler is not Running")
        except Exception:
            log.exception("Scheduler has failed to Stop")

    def active_sunrise(self):
        if self.is_running is True:
            return self.sch.active_sunrise
        else:
            return None

    def active_sunset(self):
        if self.is_running is True:
            return self.sch.active_sunset
        else:
            return None
