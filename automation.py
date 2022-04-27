from datetime import date, datetime
from pytz import timezone
from solartime import SolarTime
from time import sleep
import re


class Auto:
    def __init__(self, door, zone, longitude, latitude):
        self.longitude = longitude
        self.latitude = latitude
        self.zone = zone
        self.door = door

        self.is_running = False

    def get_world(self):
        today = datetime.today()

        year = today.year
        month = today.month
        day = today.day

        today = date(year, month, day)
        localtz = timezone(self.zone)
        lat, lon = self.latitude, self.longitude

        sun = SolarTime()
        schedule_ = sun.sun_utc(today, lat, lon)
        raw_sunset = str(schedule_['sunset'].astimezone(localtz))  # year-month-day hour:min:second-timezone
        raw_sunrise = str(schedule_['sunrise'].astimezone(localtz))  # year-month-day hour:min:second-timezone

        pattern = r" (.*?)\-"

        sunset = re.search(pattern, raw_sunset).group(1)
        sunrise = re.search(pattern, raw_sunrise).group(1)

        return {'today': today, 'sunset': sunset, 'sunrise': sunrise}

    def scheduler(self, sunrise, sunset):
        sunrise = sunrise[:len(sunrise) - 3]
        sunset = sunset[:len(sunset) - 3]
        current = datetime.now().strftime("%H:%M")

        try:
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
        except Exception as err:
            self.is_running = False
            print(f"[Automation] Scheduler Error: {err}")

    def run(self):
        while True:
            sun_data = self.get_world()
            self.scheduler(sunrise=sun_data['sunrise'], sunset=sun_data['sunset'])
