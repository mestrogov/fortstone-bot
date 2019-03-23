# -*- coding: utf-8 -*-

from app import logging
from app.remote.redis import Redis
from app.fortnite.parser.store import store as parse_store
import logging
import asyncio


def store(client, message):
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        store_file, store_hash = asyncio.get_event_loop().run_until_complete(parse_store())
        store_file_id = asyncio.get_event_loop().run_until_complete(Redis.execute(
            "GET", "fortnite:store:file_id:{0}".format(store_hash)))['details']

        if store_file_id:
            logging.info("Изображение текущего магазина уже было загружено в Telegram, "
                         "File ID: {0}.".format(store_file_id))

            client.send_photo(message.chat.id, store_file_id,
                              caption="🛒 Текущий магазин предметов в Фортнайте.")
        else:
            message = client.send_photo(message.chat.id, store_file,
                                        caption="🛒 Текущий магазин предметов в Фортнайте.")
            store_file_id = message['photo']['sizes'][-1]['file_id']

            asyncio.get_event_loop().run_until_complete(Redis.execute(
                "SET", "fortnite:store:file_id:{0}".format(store_hash), store_file_id, "EX", 86400))
    except Exception as e:
        logging.error("Произошла ошибка при выполнении команды /store.", exc_info=True)
        return e
