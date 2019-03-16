# -*- coding: utf-8 -*-

from app import logging
from app import config
from app.remote.redis import Redis
from app.fortnite.parser.store import store as parse_item_store
import logging
import asyncio


def store(client, message):
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        item_store_file, item_store_hash = asyncio.get_event_loop().run_until_complete(parse_item_store())
        item_store_file_id = asyncio.get_event_loop().run_until_complete(Redis.execute(
            "GET", "fortnite:store:file_id:{0}".format(item_store_hash)))['details']

        if item_store_file_id and not config.DEVELOPER_MODE:
            logging.info("Изображение текущего магазина предметов уже было загружено в Telegram, "
                         "File ID: {0}.".format(item_store_file_id))

            client.send_photo(message.chat.id, item_store_file_id,
                              caption="🛒 Текущий магазин предметов в Фортнайте.")
        else:
            message = client.send_photo(message.chat.id, item_store_file,
                                        caption="🛒 Текущий магазин предметов в Фортнайте.")
            item_store_file_id = message['photo']['sizes'][-1]['file_id']

            asyncio.get_event_loop().run_until_complete(Redis.execute(
                "SET", "fortnite:store:file_id:{0}".format(item_store_hash), item_store_file_id, "EX", 86400))
    except Exception as e:
        logging.error("Произошла ошибка при выполнении команды /store.", exc_info=True)
        return e
