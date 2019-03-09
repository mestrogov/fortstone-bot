# -*- coding: utf-8 -*-

from app import logging
from app import config
from app.remote.redis import Redis
from app.fortnite.parser.news import news as parse_news
import logging
import asyncio


def news(client, message):
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        news_file, news_hash = asyncio.get_event_loop().run_until_complete(parse_news())
        news_file_id = asyncio.get_event_loop().run_until_complete(Redis.execute(
            "GET", "fortnite:news:file_id:{0}".format(news_hash)))['details']
        if news_file_id and not config.DEVELOPER_MODE:
            logging.info("Изображение текущих новостей уже было загружено в Telegram, "
                         "File ID: {0}.".format(news_file_id))
            client.send_photo(message.chat.id, news_file_id,
                              caption="📰 Текущие новости Королевской Битвы и Сражения с Бурей в Фортнайте.")
        else:
            news_photo = client.send_photo(message.chat.id, news_file,
                                           caption="Текущие новости Королевской Битвы и Сражения с Бурей в Фортнайте.")
            news_file_id = news_photo['photo']['sizes'][-1]['file_id']
            asyncio.get_event_loop().run_until_complete(Redis.execute(
                "SET", "fortnite:news:file_id:{0}".format(news_hash), news_file_id, "EX", 86400))
    except Exception as e:
        logging.error("Произошла ошибка при выполнении команды /news.", exc_info=True)
        return e
