from datetime import date, datetime
from pytz import timezone
from solartime import SolarTime
from time import sleep
import schedule
import yaml
import re


with open('config.yaml') as f:
    config = yaml.safe_load(f)


def up():
    print('Up function')

def down():
    print('Down function')


def get_world():
    today = datetime.today()

    year = today.year
    month = today.month
    day = today.day

    today = date(year, month, day)
    localtz = timezone(config['timezone'])
    lat, lon = config['latitude'], config['longitude']

    sun = SolarTime()
    schedule_ = sun.sun_utc(today, lat, lon)
    raw_sunset = str(schedule_['sunset'].astimezone(localtz))  # year-month-day hour:min:second-timezone
    raw_sunrise = str(schedule_['sunrise'].astimezone(localtz))  # year-month-day hour:min:second-timezone

    pattern = r" (.*?)\-"

    sunset = re.search(pattern, raw_sunset).group(1)
    sunrise = re.search(pattern, raw_sunrise).group(1)

    return {'today': today, 'sunset': sunset, 'sunrise': sunrise}


def scheduler(sunrise, sunset):
    sunrise = sunrise[:len(sunrise) - 3]
    sunset = sunset[:len(sunset) - 3]
    print(sunrise)
    print(sunset)

    schedule.every().day.at(sunrise).do(print('f'))  # check if it needs number:number instead of number:number:number
    schedule.every().day.at(sunset).do(print('d'))  # check if it needs number:number instead of number:number:number

    while True:
        schedule.run_pending()
        sleep(60)  # wait one minute


def run():
    sun_data = get_world()

    scheduler(sunrise=sun_data['sunrise'], sunset=sun_data['sunset'])


run()
