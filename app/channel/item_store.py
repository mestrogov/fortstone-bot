# -*- coding: utf-8 -*-

from app import logging
from app import config
from app.remote.redis import Redis
from app.fortnite.parser.store import store as parse_item_store
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
    last_item_store_hash = (await Redis.execute("GET", "fortnite:store:channel"))['details']
    item_store_file, item_store_hash = await parse_item_store()

    if not last_item_store_hash or last_item_store_hash != item_store_hash or config.DEVELOPER_MODE:
        logging.info("Похоже, что магазин предметов в Фортнайте был обновлен. Публикуется его изображение в канал, "
                     "указанный в конфигурационном файле.")

        client.send_photo(config.CHANNEL_ID, item_store_file,
                          caption="🛒 Магазин предметов в Фортнайте был обновлен. #магазин")
        """
        Не работает из-за того, что MTPROTO API запрещает отправку голосований от бота

        client.send_poll(config.CHANNEL_ID, question="Оцените магазин предметов в Фортнайте сегодня.",
                         options=["👍🏼 Мне нравится", "👉🏻 Есть некоторые предметы, которые мне нравятся",
                                  "👎🏼 Мне не нравится"], disable_notification=True)
        """

        await Redis.execute("SET", "fortnite:store:channel", item_store_hash, "EX", 86400)
