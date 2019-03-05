# -*- coding: utf-8 -*-

from app import logging
from app.api.parsers.status import status as parse_services_status
import logging
import asyncio


def status(client, message):
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        f_status_message = asyncio.get_event_loop().run_until_complete(parse_services_status())
        client.send_message(message.chat.id, f_status_message, disable_web_page_preview=True)
    except Exception as e:
        logging.error("Произошла ошибка при выполнении команды /status.", exc_info=True)
        return e
