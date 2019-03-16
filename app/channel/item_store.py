# -*- coding: utf-8 -*-

from app import logging
from app import config
from app.remote.redis import Redis
from app.fortnite.parser.store import store as parse_item_store
from app.utils import convert_to_moscow
from pyrogram import InputMediaPhoto
from itertools import zip_longest
from datetime import datetime
from time import sleep, time
import logging
import asyncio


def post(client):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    while True:
        try:
            asyncio.get_event_loop().run_until_complete(post_async(client))
        except Exception:
            logging.error("Произошла ошибка при публикации ежедневного магазина предметов в канал.", exc_info=True)

        sleep(15)


# Делаем dict из list'а (метод HGETALL в Redis возвращает list); взято отсюда: https://stackoverflow.com/a/6900977
async def redis_hgetall(key):
    return dict(zip_longest(*[iter((await Redis.execute("HGETALL", key))['details'])] * 2, fillvalue=""))


async def post_async(client):
    item_store_channel = (await redis_hgetall("fortnite:store:channel"))
    item_store_file, item_store_hash = await parse_item_store()

    item_store_caption = "🛒 Магазин предметов в Фортнайте был обновлен. #магазин"
    item_store_caption_edited = f"{item_store_caption}\n\n__Магазин предметов после оригинальной публикации " \
                                "сообщения был обновлен в {} по московскому времени.__"

    if not item_store_channel or item_store_channel['hash'] != item_store_hash or config.DEVELOPER_MODE:
        logging.info("Магазин предметов в Фортнайте был обновлен. Публикуется его изображение в канал, "
                     "указанный в конфигурационном файле.")

        try:
            assert item_store_channel['chat_id']
            assert item_store_channel['message_id']
            assert item_store_channel['time']

            if int(time()) - int(item_store_channel['time']) < 3600:
                logging.info("Последний пост с магазином предметов был опубликован в канал меньше, "
                             "чем час назад, поэтому сообщение было отредактировано обновленным магазином.")

                message = client.edit_message_media(
                    int(item_store_channel['chat_id']), int(item_store_channel['message_id']),
                    media=InputMediaPhoto(item_store_file, caption=item_store_caption_edited.format(
                        convert_to_moscow(datetime.utcnow()).strftime("%H:%M:%S")
                    )))
            else:
                raise AssertionError
        except (AssertionError, TypeError, KeyError):
            message = client.send_photo(config.CHANNEL_ID, item_store_file, caption=item_store_caption)

        await Redis.execute("HSET", "fortnite:store:channel", "hash", item_store_hash, "chat_id", message['chat']['id'],
                            "message_id", message['message_id'], "time", int(time()))
        await Redis.execute("EXPIRE", "fortnite:store:channel", 86400)

        """
        Раскомментировать, когда MTPROTO API будет разрешать отправлять ботам голосования 

        client.send_poll(config.CHANNEL_ID, question="Оцените магазин предметов в Фортнайте сегодня.",
                         options=["👍🏼 Мне нравится", "👉🏻 Есть некоторые предметы, которые мне нравятся",
                                  "👎🏼 Мне не нравится"], disable_notification=True)
        """
