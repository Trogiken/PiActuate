from door import Door
from datetime import date, datetime
from pytz import timezone
from solartime import SolarTime
from time import sleep
import schedule
import yaml
import re


class Auto:
    with open('config.yaml') as f:
        config = yaml.safe_load(f)

    door = Door()

    def get_world(self):
        today = datetime.today()

        year = today.year
        month = today.month
        day = today.day

        today = date(year, month, day)
        localtz = timezone(self.config['timezone'])
        lat, lon = self.config['latitude'], self.config['longitude']

        sun = SolarTime()
        schedule_ = sun.sun_utc(today, lat, lon)
        raw_sunset = str(schedule_['sunset'].astimezone(localtz))  # year-month-day hour:min:second-timezone
        raw_sunrise = str(schedule_['sunrise'].astimezone(localtz))  # year-month-day hour:min:second-timezone

        pattern = r" (.*?)\-"

        sunset = re.search(pattern, raw_sunset).group(1)
        sunrise = re.search(pattern, raw_sunrise).group(1)

        return {'today': today, 'sunset': sunset, 'sunrise': sunrise}

    def up(self):
        response = self.door.move('up')
        if response['check']:
            print(f"Door INFO: {response['msg']}")
        elif not response['check']:
            print(f"Door ERROR: {response['msg']}")

    def down(self):
        response = self.door.move('down')
        if response['check']:
            print(f"Door INFO: {response['msg']}")
        elif not response['check']:
            print(f"Door ERROR: {response['msg']}")

    def scheduler(self, sunrise, sunset):

        schedule.every().at(sunrise).do(self.up())  # check if it needs number:number instead of number:number:number
        schedule.every().at(sunset).do(self.down())  # check if it needs number:number instead of number:number:number

        while True:
            schedule.run_pending()
            sleep(60)  # wait one minute

    def run(self):
        sun_data = self.get_world()

        self.scheduler(sunrise=sun_data['sunrise'], sunset=sun_data['sunset'])
