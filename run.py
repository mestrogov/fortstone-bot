# -*- coding: utf-8 -*-

from app import config
from app.remote.redis import Redis as redis
from app.telegram.app import get_client as telegram_get_client
from app.fortnite.app import get_client as fortnite_get_client
from app.channel.item_store import post as channel_store_poster
from threading import Thread, Timer
from time import sleep
import logging
import asyncio


if __name__ == "__main__":
    try:
        asyncio.get_event_loop().run_until_complete(redis.connection())

        telegram_client = telegram_get_client()
        Thread(target=telegram_client.start, name="telegram_client").start()

        # Telegram клиенту нужно немного времени, чтобы запуститься
        sleep(1)

        # fortnite_client = fortnite_get_client()

        # Если в конфиге указан ID канала, то запускаем поток с публикованием ежедневного магазина
        if config.CHANNEL_ID:
            Timer(15, channel_store_poster, [telegram_client]).start()
        else:
            logging.info("ID канала не указан в конфигурационном файле, постинг магазина предметов в канал "
                         "не будет работать.")
    except Exception as e:
        logging.critical("Произошла ошибка в работе приложения.", exc_info=True)
