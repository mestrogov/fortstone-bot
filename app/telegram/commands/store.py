# -*- coding: utf-8 -*-

from app import logging
from app.api.parsers.store import store as parse_item_store
import logging
import asyncio


def store(client, message):
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        item_store_file = asyncio.get_event_loop().run_until_complete(parse_item_store())
        client.send_photo(message.from_user.id, item_store_file,
                          caption="🛒 Ежедневный магазин предметов в Фортнайте.")
        client.send_document(message.from_user.id, item_store_file,
                             caption="🛒 Ежедневный магазин предметов в Фортнайте в высоком разрешении.")
    except Exception as e:
        logging.error("Произошла ошибка при выполнении команды /status.", exc_info=True)
        return e
