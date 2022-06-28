""""""
import calendar
import json
import logging
import pprint

import pytz
from dotenv import find_dotenv, load_dotenv
from pytz import timezone
from astral import LocationInfo
from datetime import datetime, timedelta
from astral.sun import sun
from astral.geocoder import database, lookup, add_locations
from astral import LocationInfo

from enum import Enum
from os import environ as env

ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

logging.basicConfig(level=env.get("LOGLEVEL", "INFO"), format='%(levelname)s - %(message)s')

planets_with_symbols = {'Saturn': '♄', 'Jupiter': '♃', 'Mars': '♂', 'Sun': '☉', 'Venus': '♀', 'Mercury': '☿',
                        'Moon': '☾'}

with open("planetaryhours.json") as file:
    ph = json.load(file)

astral_db = database()


def check_location(name, region, tz, lat, long):
    """
    helper function to make sure data to grab sunrise/sunset from astral module is correct
    takes in data for location, returns book
    :param name: City name
    :param region: Region name
    :param tz: timezone Continent/City
    :param lat: latitude
    :param long: longitude
    :return: True or false
    """
    if not (-90 <= lat <= 90):
        return False
    elif not (-180 <= long <= 180):
        return False
    elif tz not in pytz.all_timezones:
        return False
    else:
        return True


def planetary_hours(date, sunrise, sunset, daylight_hours, night_hours):
    # day hours
    result = []
    current = sunrise
    for hour in range(12):
        result.append((current , (current + daylight_hours)))
        current = current + daylight_hours
    # pprint.pprint(result)
    # result.clear()
    # print("sunset")
    for hour in range(12):
        result.append((current , (current + night_hours)))
        current = current + night_hours
    # pprint.pprint(result)
    day = calendar.day_name[date.weekday()]  # 'Wednesday'
    wrapped = zip(ph[day], result)
    return (list(wrapped))


def get_adjusted_hours(location, date=datetime.today(),tz=False):
    """

    :param location
    :param date
    :return dict of {day:(sunrise time,day hours),night:(sunset time, night hours)}

    """
    adjusted = False
    s = sun(location.observer,
            date=date,
            tzinfo=pytz.timezone(location.timezone))
    if date.hour < s['sunrise'].hour:
        # between midnight and sunrise, dial back one day
        logging.debug("adjusting for late hours")
        date = date - timedelta(days=1)
        s = sun(location.observer,
                date=date,
                tzinfo=pytz.timezone(location.timezone))
        adjusted = True
    daylight_seconds = s['sunset'] - s['sunrise']
    daylight_hours = daylight_seconds / 12
    next_s = sun(location.observer,
                 date=date + timedelta(days=1),
                 tzinfo=pytz.timezone(location.timezone))
    night_seconds = next_s['sunrise'] - s['sunset']
    night_hours = night_seconds / 12
    sunrise = s['sunrise']
    sunset = s['sunset']


    logging.debug(
        f"{str(date)}\nday:{str(daylight_hours), str(daylight_seconds)}\nnight:{str(night_hours), str(night_seconds)}")

    return({"date":(date),'yesterday':adjusted,
         'planetaryhours':planetary_hours(date, sunrise.replace(tzinfo=None), sunset, daylight_hours, night_hours)})


def check_city(name):

    try:
        return lookup(name, astral_db)
    except KeyError:
        return None


# add_locations("Somewhere,Secret Location,UTC,24°28'N,39°36'E", db)
# print(get_adjusted_hours(check_city("riyadh"), datetime(2022, 6, 20, 2)))
