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


def convert_date_into_words(date):
    months_translated_dict = {
        "January": "Января",
        "February": "Февраля",
        "March": "Марта",
        "April": "Апреля",
        "May": "Мая",
        "June": "Июня",
        "July": "Июля",
        "August": "Августа",
        "September": "Сентября",
        "October": "Октября",
        "November": "Ноября",
        "December": "Декабря"
    }

    date = date.strftime("%d %B %Y").split(" ")
    date[1] = date[1].replace(date[1], months_translated_dict[date[1]])

    return "{0} года".format(" ".join(date))
