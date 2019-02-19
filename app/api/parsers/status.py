# -*- coding: utf-8 -*-

from app import logging
from app.remote.redis import Redis
from app.api.utils import translations
import logging
import json
import requests


async def status():
    try:
        api_status_url = "https://status.epicgames.com/api/v2/summary.json"

        f_status = (await Redis.execute("GET", "fortnite:status"))['details']
        if not f_status:
            f_status = requests.get(api_status_url).json()
            await Redis.execute("SET", "fortnite:status", json.dumps(f_status), "EX", 30)
        else:
            f_status = json.loads(f_status)

        if f_status['status']['description'] == "All Systems Operational":
            f_status_message = "✅ Сервисы Epic Games работают в штатном режиме."
        elif f_status['status']['description'] == "Partial System Outage":
            f_status_message = "⚠️ Некоторые из сервисов Epic Games работают с перебоями или вовсе не работают."
        elif f_status['status']['description'] == "Major Service Outage":
            f_status_message = "❌ Большинство из сервисов Epic Games работают с перебоями или вовсе не работают."
        else:
            f_status_message = "⁉️ С сервисами Epic Games происходит нечто странное, похоже на какую-то " \
                               "нештатную ситуацию."
        if f_status['components']:
            broken_services = [service for service in f_status['components'] if not service['status'] == "operational"]
            if broken_services:
                f_status_message = "{0}\n\n⛔️ Сервисы, которые работают с перебоями или вовсе не работают:".format(
                    f_status_message)
                for num, service in enumerate(f_status['components']):
                    if not service['status'] == "operational" and not service['group']:
                        f_status_message = "{0}\n**{1}.** {2}, состояние: **{3}**.".format(
                            f_status_message, num+1, translations.translate_service_name(service['name']),
                            translations.translate_service_status(service['status']))
        if f_status['scheduled_maintenances']:
            f_status_message = "{0}\n\n🕰 Запланированные технические работы:".format(f_status_message)
            for num, maintenance in enumerate(f_status['scheduled_maintenances']):
                f_status_message = "{0}\n**{1}.** {2}, запланировано начало на **{3}** в **{4}**, " \
                                   "окончание на **{5}** в **{6}** UTC (московское время больше на 3 часа).".\
                    format(f_status_message, num+1, maintenance['name'])
        f_status_message = "{0}\n\nУзнать подробную информацию о работе сервисов Epic Games можно " \
                           "[здесь](https://status.epicgames.com/).".format(f_status_message)

        return f_status_message
    except Exception as e:
        logging.error("Произошла ошибка при выполнении команды /status.", exc_info=True)
        return "Произошла ошибка при попытке получения статуса сервисов Epic Games."
