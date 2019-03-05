# -*- coding: utf-8 -*-

from app import logging
from app import config
from app.remote.redis import Redis
from app.api.parsers.store import store as parse_item_store
from time import sleep
import logging
import asyncio


def post(client):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    asyncio.get_event_loop().run_until_complete(post_async(client))


async def post_async(client):
    while True:
        last_item_store_hash = (await Redis.execute("GET", "fortnite:store:channel"))['details']
        item_store_file, item_store_hash = (await parse_item_store())

        if not last_item_store_hash or last_item_store_hash != item_store_hash:
            logging.info("Похоже, что магазин предметов в Фортнайте был обновлен. Публикуется изображение в канал.")

            client.send_photo(config.CHANNEL_ID, item_store_file,
                              caption="🛒 Магазин предметов в Фортнайте был обновлен. #магазин")
            await Redis.execute("SET", "fortnite:store:channel", item_store_hash, "EX", 86400)
        sleep(15)
