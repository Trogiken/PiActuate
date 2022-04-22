from datetime import date, timedelta, datetime
from pytz import timezone
from solartime import SolarTime
import requests
import yaml


def automation():
    with open('config.yaml') as f:
        config = yaml.safe_load(f)

    city = config['city']
    country = config['country']

    url = "https://nominatim.openstreetmap.org/?addressdetails=1&q=" + city + "+" + country +"&format=json&limit=1"

    response = requests.get(url).json()

    yesterday = datetime.today() - timedelta(1)

    year = yesterday.year
    month = yesterday.month
    day = yesterday.day

    today = date(year, month, day)
    localtz = timezone(config['timezone'])
    lat, lon = float(response[0]["lat"]), float(response[0]["lon"])

    sun = SolarTime()
    schedule = sun.sun_utc(today, lat, lon)
    sunset = schedule['sunset'].astimezone(localtz)

    return sunset


print(automation())
