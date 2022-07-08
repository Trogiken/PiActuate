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
            current = datetime.now().strftime("%H:%M")

            self.active_sunrise = sunrise
            self.active_sunset = sunset

            log.info(f"Sunset set to [{sunset}]")
            log.info(f"Sunrise set to [{sunrise}]")
            log.info(f"Current time [{current}]")

            while True:
                if sunrise <= current < sunset:  # Check if comparison works
                    if not self.door.status() == 'up':
                        self.door.move('up')
                        log.info("Door Called Up")
                        break
                else:
                    if not self.door.status() == 'down':
                        self.door.move('down')
                        log.info("Door Called Down")
                        break
                sleep(300)
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

                self.sch = None
                self.is_running = False
                log.info("Scheduler has stopped Running")
            else:
                log.warning("Scheduler is not Running")
        except Exception:
            log.exception("Scheduler has failed to Stop")

    def active_sunrise(self):
        if self.is_running is True:
            return self.sch.active_sunrise  # DEBUG
        else:
            return None

    def active_sunset(self):
        if self.is_running is True:
            return self.sch.active_sunset  # DEBUG
        else:
            return None
