from datetime import date, datetime, timedelta
from pytz import timezone
from solartime import SolarTime
from time import sleep
import re


class Auto:
    def __init__(self, door, zone, longitude, latitude, sunrise_offset=0, sunset_offset=0):
        self.longitude = longitude
        self.latitude = latitude
        self.sunrise_offset = sunrise_offset
        self.sunset_offset = sunset_offset
        self.zone = zone
        self.door = door

        self.is_running = False

    def get_world(self):
        today = datetime.today()
        rise_offset = timedelta(minutes=self.sunrise_offset)
        set_offset = timedelta(minutes=self.sunset_offset)

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

    def scheduler(self, sunrise, sunset):
        sunrise = sunrise[:len(sunrise) - 3]
        sunset = sunset[:len(sunset) - 3]
        current = datetime.now().strftime("%H:%M")

        while True:
            self.is_running = True
            if current >= sunrise:  # Check if comparison works
                if not self.door.status()['position'] == 'up':
                    msg = self.door.move('up')
                    print(f"[Automation] Door Movement: {msg}")
                    break
            elif current >= sunset:  # Check if comparison works
                if not self.door.status()['position'] == 'down':
                    msg = self.door.move('down')
                    print(f"[Automation] Door Movement: {msg}")
                    break
            sleep(300)

    def run(self):
        while True:
            try:
                sun_data = self.get_world()
                self.scheduler(sunrise=sun_data['sunrise'], sunset=sun_data['sunset'])
            except Exception as err:
                print(f"[Automation] ERROR: {err}")
                return err
