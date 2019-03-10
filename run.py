# -*- coding: utf-8 -*-

from app import config
from app.remote.redis import Redis as redis
from app.telegram.app import get_client as telegram_get_client
from app.fortnite.app import get_session as fortnite_get_session
from app.channel.item_store import post as channel_store_poster
from app.channel.news import post as channel_news_poster
from threading import Thread
from time import sleep
import logging
import asyncio


if __name__ == "__main__":
    try:
        asyncio.get_event_loop().run_until_complete(redis.connection())

        telegram_client = telegram_get_client()
        Thread(target=telegram_client.start, name="telegram_client").start()
        # Клиенту необходимо немного времени, чтобы запуститься
        sleep(1)

        fortnite_session = fortnite_get_session()

        # Если в конфиге указан ID канала, то запускаем поток с публикованием различной информации в канал
        if config.CHANNEL_ID:
            Thread(target=channel_store_poster, args=(telegram_client,), name="channel_store_poster").start()
            Thread(target=channel_news_poster, args=(telegram_client,), name="channel_news_poster").start()
        else:
            logging.info("Так как в конфигурациионом файле не указан ID канала, постинг различной информации "
                         "в канал не будет работать.")
    except Exception as e:
        logging.critical("Произошла ошибка в работе приложения.", exc_info=True)
