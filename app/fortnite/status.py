# -*- coding: utf-8 -*-

from app import logging
from app import utils
from app.remote.redis import Redis
from app.fortnite.utils import status_translations
import logging
import json
import requests


async def status():
    try:
        api_status_url = "https://status.epicgames.com/api/v2/summary.json"

        f_status = (await Redis.execute("GET", "fortnite:status"))['details']
        if f_status:
            f_status = json.loads(f_status)
        else:
            f_status = requests.get(api_status_url).json()
            await Redis.execute("SET", "fortnite:status", json.dumps(f_status), "EX", 20)

        # Переводим глобальное состояние сервисов на русский
        message = status_translations.translate_global_status(f_status['status']['description'])

        # Проверяем, есть ли информация о сервисах, которые не работают в штатном режиме
        if f_status['components']:
            broken_services = [service for service in f_status['components'] if not service['status'] == "operational"]
            if broken_services:
                message = "{0}\n\n⛔️ Сервисы, которые **не** работают в штатном режиме:".format(message)

                num = 1
                for service in f_status['components']:
                    if not service['status'] == "operational" and not service['group']:
                        message = "{0}\n{1}. {2}, состояние: **{3}**.".format(
                            message, num, status_translations.translate_service_name(service['name']),
                            status_translations.translate_service_status(service['status'])
                        )
                        num += 1

        # Проверяем, есть ли информация о происшествиях
        if f_status['incidents']:
            message = "{0}\n\n❗️ Происшествия, связанные с сервисами:".format(message)

            for num, incident in enumerate(f_status['incidents']):
                message = "{0}\n{1}. {2}, [подробнее]({3}).".format(message, num+1, incident['name'],
                                                                    incident['shortlink'])

        # Проверяем, есть ли информация о запланированных технических работах
        if f_status['scheduled_maintenances']:
            message = "{0}\n\n🕰 Запланированные технические работы:".format(message)

            for num, maintenance in enumerate(f_status['scheduled_maintenances']):
                scheduled_for_date = utils.convert_to_moscow(utils.convert_iso_time(maintenance['scheduled_for']))
                scheduled_until_date = utils.convert_to_moscow(utils.convert_iso_time(maintenance['scheduled_until']))

                message = "{0}\n{1}. [{2}]({3}), запланировано начало на **{4}** в **{5}**, " \
                          "окончание на **{6}** в **{7}** по московскому времени.".\
                    format(message, num+1, maintenance['name'], maintenance['shortlink'],
                           scheduled_for_date.strftime("%d.%m.%y"), scheduled_for_date.strftime("%H:%M"),
                           scheduled_until_date.strftime("%d.%m.%y"), scheduled_until_date.strftime("%H:%M"))

        message = "{0}\n\nУзнать более подробную информацию о работе сервисов Epic Games можно " \
                  "[здесь](https://status.epicgames.com/).".format(message)

        return message
    except Exception as e:
        logging.error("Произошла ошибка при попытке парсирования статуса сервисов Epic Games.", exc_info=True)
        return "Произошла ошибка при попытке парсирования статуса сервисов Epic Games."
