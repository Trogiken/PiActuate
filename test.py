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
    state = config['state']

    if state:
        url = f"https://nominatim.openstreetmap.org/?addressdetails=1&q={city}+{state}+{country}&format=json&limit=1"
    if not state:
        url = f"https://nominatim.openstreetmap.org/?addressdetails=1&q={city}+{country}&format=json&limit=1"

    try:
        response = requests.get(url).json()
    except Exception:
        return

    today = datetime.today()

    year = today.year
    month = today.month
    day = today.day

    today = date(year, month, day)
    localtz = timezone(config['timezone'])
    lat, lon = float(response[0]["lat"]), float(response[0]["lon"])

    sun = SolarTime()
    schedule = sun.sun_utc(today, lat, lon)
    sunset = schedule['sunset'].astimezone(localtz)
    sunrise = schedule['sunrise'].astimezone(localtz)

    return {'sunset': sunset, 'sunrise': sunrise}


data = automation()
print(f"Sunrise: {data['sunrise']}\nSunset : {data['sunset']}")
