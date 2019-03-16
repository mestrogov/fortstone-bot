# -*- coding: utf-8 -*-

from app import logging
from app import config
from app.remote.redis import Redis
from app.fortnite.parser.news import news as parse_news
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
            logging.error("Произошла ошибка при публикации новостей в канал.", exc_info=True)

        sleep(15)


# Делаем dict из list'а (метод HGETALL в Redis возвращает list); взято отсюда: https://stackoverflow.com/a/6900977
async def redis_hgetall(key):
    return dict(zip_longest(*[iter((await Redis.execute("HGETALL", key))['details'])] * 2, fillvalue=""))


async def post_async(client):
    news_channel = (await redis_hgetall("fortnite:news:channel"))
    news_file, news_hash = await parse_news()

    news_caption = "📰 Новости Королевской Битвы и/или Сражения с Бурей были обновлены. #новости"
    news_caption_edited = f"{news_caption}\n\n__Новости после оригинальной публикации " \
                          "сообщения были обновлены в {} по московскому времени.__"

    if not news_channel or news_channel['hash'] != news_hash or config.DEVELOPER_MODE:
        logging.info("Новости в Фортнайте были обновлены. Публикуется их изображение в канал, "
                     "указанный в конфигурационном файле.")

        try:
            assert news_channel['chat_id']
            assert news_channel['message_id']
            assert news_channel['time']

            if int(time()) - int(news_channel['time']) < 3600:
                logging.info("Последний пост с новостями был опубликован в канал меньше, чем час назад, поэтому "
                             "сообщение было отредактировано обновленными новостями.")

                message = client.edit_message_media(
                    int(news_channel['chat_id']), int(news_channel['message_id']),
                    media=InputMediaPhoto(news_file, caption=news_caption_edited.format(
                        convert_to_moscow(datetime.utcnow()).strftime("%H:%M:%S")
                    )))
            else:
                raise AssertionError
        except (AssertionError, TypeError, KeyError):
            message = client.send_photo(config.CHANNEL_ID, news_file, caption=news_caption)

        await Redis.execute("HSET", "fortnite:news:channel", "hash", news_hash, "chat_id", message['chat']['id'],
                            "message_id", message['message_id'], "time", int(time()))
        await Redis.execute("EXPIRE", "fortnite:news:channel", 604800)
