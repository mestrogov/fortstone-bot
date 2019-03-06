# -*- coding: utf-8 -*-

from datetime import datetime
import pytz


def parse_as_boolean(arg):
    if str(arg).lower() in ["true", "1"]:
        return True
    else:
        return False


def convert_iso_time(isotime):
    return datetime.strptime(isotime, '%Y-%m-%dT%H:%M:%S.%fZ')


def convert_to_moscow(utctime):
    return pytz.utc.localize(utctime).astimezone(pytz.timezone("Europe/Moscow"))
