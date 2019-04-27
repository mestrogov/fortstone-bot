# -*- coding: utf-8 -*-

from app import logging
from app import config
from app.remote.redis import Redis
from app.fortnite.store import store as parse_store
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
            logging.error("Произошла ошибка при публикации магазина в канал.", exc_info=True)

        sleep(30)


# Делаем dict из list'а (метод HGETALL в Redis возвращает list); взято отсюда: https://stackoverflow.com/a/6900977
async def redis_hgetall(key):
    return dict(zip_longest(*[iter((await Redis.execute("HGETALL", key))['details'])] * 2, fillvalue=""))


async def post_async(client):
    store_channel = (await redis_hgetall("fortnite:store:channel"))
    store_file, store_hash = await parse_store()

    store_caption = "🛒 Магазин предметов в Фортнайте был обновлен. #магазин"
    store_caption_edited = f"{store_caption}\n\n__Магазин после оригинальной публикации " \
                           "сообщения был обновлен в {} по московскому времени.__"

    if not store_channel or store_channel['hash'] != store_hash:
        logging.info("Магазин в Фортнайте был обновлен. Публикуется его изображение в канал, "
                     "указанный в конфигурационном файле.")

        try:
            assert store_channel['chat_id']
            assert store_channel['message_id']
            assert store_channel['time']

            if int(time()) - int(store_channel['time']) < 7200:
                logging.info("Последний пост с магазином был опубликован в канал меньше, чем 2 часа назад, поэтому "
                             "сообщение было отредактировано обновленным магазином.")

                message = client.edit_message_media(
                    int(store_channel['chat_id']), int(store_channel['message_id']),
                    media=InputMediaPhoto(store_file, caption=store_caption_edited.format(
                        convert_to_moscow(datetime.utcnow()).strftime("%H:%M:%S")
                    )))
            else:
                raise AssertionError
        except (AssertionError, TypeError, KeyError):
            message = client.send_photo(config.CHANNEL_ID, store_file, caption=store_caption)

            client.send_poll(config.CHANNEL_ID, question="Оцените текущий магазин предметов в Фортнайте.",
                             options=[
                                 "👍 Мне нравится весь магазин предметов",
                                 "🙂 Мне нравятся некоторые предметы",
                                 "👎 Мне не нравится весь магазин предметов"
                             ], disable_notification=True)

        await Redis.execute("HSET", "fortnite:store:channel", "hash", store_hash, "chat_id", message['chat']['id'],
                            "message_id", message['message_id'], "time", int(time()))
        await Redis.execute("EXPIRE", "fortnite:store:channel", 172800)
