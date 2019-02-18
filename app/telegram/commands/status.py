# -*- coding: utf-8 -*-

from app import logging
from app.remote.redis import Redis
import logging
import json
import requests
import asyncio


def status(client, message):
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        status_url = "https://status.epicgames.com/api/v2/summary.json"

        f_status = asyncio.get_event_loop().run_until_complete(Redis.execute("GET", "fortnite:status"))['details']
        if not f_status:
            f_status = requests.get(status_url).json()
            asyncio.get_event_loop().run_until_complete(
                Redis.execute("SET", "fortnite:status", json.dumps(f_status), "EX", 30))
        else:
            f_status = json.loads(f_status)

        if f_status['status']['description'] == "All Systems Operational":
            f_status_message = "✅ Сервисы Epic Games работают в штатном режиме."
        elif f_status['status']['description'] == "Partial System Outage":
            f_status_message = "⚠️ Сервисы Epic Games испытывают затруднения, возможны некоторые проблемы при " \
                               "взаимодействии с ними. Подробная информация находится " \
                               "[здесь](https://status.epicgames.com/)."
        elif f_status['status']['description'] == "Major Service Outage":
            f_status_message = "❌ Сервисы Epic Games испытывают серьезные проблемы, могут возникать серьезные " \
                               "проблемы при взаимодействии с ними. Подробная информация находится " \
                               "[здесь](https://status.epicgames.com/)."
        else:
            f_status_message = "⁉️ С сервисами Epic Games происходит нечто странное, похоже на какую-то " \
                               "нештатную ситуацию (возможно, что это всего лишь ложь). " \
                               "Подробная информация находится [здесь](https://status.epicgames.com/)."
        if f_status['scheduled_maintenances']:
            f_status_message = "\n\n🕰 Запланированные технические работы:\n"
            num = 0
            for maintenance in f_status['scheduled_maintenances']:
                f_status_message = "{0}\n**{1}.** {2}".format(f_status_message, num, maintenance['name'])
                num += 1

        client.send_message(message.from_user.id, f_status_message)
    except Exception as e:
        logging.error("Произошла ошибка при выполнении команды /status.", exc_info=True)
        return e
