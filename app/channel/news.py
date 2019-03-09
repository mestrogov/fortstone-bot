# -*- coding: utf-8 -*-

from app import logging
from app import config
from app.remote.redis import Redis
from app.fortnite.parser.news import news as parse_news
from time import sleep
import logging
import asyncio


def post(client):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    while True:
        asyncio.get_event_loop().run_until_complete(post_async(client))
        sleep(15)


async def post_async(client):
    last_news_hash = (await Redis.execute("GET", "fortnite:news:channel"))['details']
    news_file, news_hash = await parse_news()

    if not last_news_hash or last_news_hash != news_hash or config.DEVELOPER_MODE:
        logging.info("Похоже, что новости в Фортнайте были обновлены. Публикуется их изображение в канал, "
                     "указанный в конфигурационном файле.")

        client.send_photo(config.CHANNEL_ID, news_file,
                          caption="📰 Новости Королевской Битвы и/или Сражения с Бурей были обновлены. #новости")

        await Redis.execute("SET", "fortnite:news:channel", news_hash, "EX", 86400)
