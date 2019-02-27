# -*- coding: utf-8 -*-

from app import logging
from app.remote.redis import Redis
from app.api.utils import translations
import logging
import pytz
import datetime
import json
import requests


async def status():
    try:
        api_status_url = "https://status.epicgames.com/api/v2/summary.json"

        f_status = (await Redis.execute("GET", "fortnite:status"))['details']
        if not f_status:
            f_status = requests.get(api_status_url).json()
            await Redis.execute("SET", "fortnite:status", json.dumps(f_status), "EX", 15)
        else:
            f_status = json.loads(f_status)

        if f_status['status']['description'] == "All Systems Operational":
            f_status_message = "✅ Сервисы Epic Games работают в штатном режиме."
        elif f_status['status']['description'] == "Partially Degraded Service":
            f_status_message = "〽️ Некоторые из сервисов Epic Games работают с ухудшенной производительностью."
        elif f_status['status']['description'] == "Partial System Outage":
            f_status_message = "⚠️ Некоторые из сервисов Epic Games частично недоступны."
        elif f_status['status']['description'] == "Major Service Outage":
            f_status_message = "❌ Большинство из сервисов Epic Games недоступны."
        else:
            f_status_message = "⁉️ С сервисами Epic Games происходит нечто странное (нештатная ситуация)."
        if f_status['components']:
            broken_services = [service for service in f_status['components'] if not service['status'] == "operational"]
            if broken_services:
                f_status_message = "{0}\n\n⛔️ Сервисы, которые **не** работают в штатном режиме:".format(
                    f_status_message)
                num = 1
                for service in f_status['components']:
                    if not service['status'] == "operational" and not service['group']:
                        f_status_message = "{0}\n{1}. {2}, состояние: **{3}**.".format(
                            f_status_message, num, translations.translate_service_name(service['name']),
                            translations.translate_service_status(service['status']))
                        num += 1
        if f_status['incidents']:
            f_status_message = "{0}\n\n❗️ Происшествия, связанные с сервисами:".format(f_status_message)
            for num, incident in enumerate(f_status['incidents']):
                f_status_message = "{0}\n{1}. {2}, [подробнее]({3}).".format(
                    f_status_message, num+1, incident['name'], incident['shortlink'])
        if f_status['scheduled_maintenances']:
            f_status_message = "{0}\n\n🕰 Запланированные технические работы:".format(f_status_message)
            for num, maintenance in enumerate(f_status['scheduled_maintenances']):
                scheduled_for_date = pytz.utc.localize(datetime.datetime.strptime(maintenance['scheduled_for'],
                                                                                  "%Y-%m-%dT%H:%M:%S.%fZ")).\
                    astimezone(pytz.timezone("Europe/Moscow"))
                scheduled_until_date = pytz.utc.localize(datetime.datetime.strptime(maintenance['scheduled_until'],
                                                                                    "%Y-%m-%dT%H:%M:%S.%fZ")).\
                    astimezone(pytz.timezone("Europe/Moscow"))
                f_status_message = "{0}\n{1}. [{2}]({3}), запланировано начало на **{4}** в **{5}**, " \
                                   "окончание на **{6}** в **{7}** по МСК.".\
                    format(f_status_message, num+1, maintenance['name'], maintenance['shortlink'],
                           scheduled_for_date.strftime("%d.%m.%y"), scheduled_for_date.strftime("%H:%M"),
                           scheduled_until_date.strftime("%d.%m.%y"), scheduled_until_date.strftime("%H:%M"))
        f_status_message = "{0}\n\nУзнать подробную информацию о работе сервисов Epic Games можно " \
                           "[здесь](https://status.epicgames.com/).".format(f_status_message)

        return f_status_message
    except Exception as e:
        logging.error("Произошла ошибка при попытке парсирования статуса сервисов Epic Games.", exc_info=True)
        return "Произошла ошибка при попытке парсирования статуса сервисов Epic Games."
