# -*- coding: utf-8 -*-

from app import logging
from app import config
from app.remote.redis import Redis
from app.fortnite.wrapper.fortnite import Fortnite
from app import utils
from tempfile import NamedTemporaryFile
from PIL import Image, ImageDraw, ImageFont, ImageOps
from hashlib import sha1
from os.path import isfile
import json
import pytz
import datetime
import logging
import math
import requests
import asyncio


async def news():
    try:
        news_json = (await Redis.execute("GET", "fortnite:news:json"))['details']
        if news_json and not config.DEVELOPER_MODE:
            news_json = json.loads(news_json)
        else:
            news_json = Fortnite.ingame_news()
            await Redis.execute("SET", "fortnite:news:json", json.dumps(news_json), "EX", 20)

        news_hash = sha1(
            str(news_json['battleroyale']['last_modified'] + news_json['savetheworld']['last_modified']).encode("UTF-8")
        ).hexdigest()

        news_file = (await Redis.execute("GET", "fortnite:news:file:{0}".format(news_hash)))['details']
        if news_file and isfile(news_file) and not config.DEVELOPER_MODE:
            logging.info("Изображение текущих новостей уже сгенерировано, файл: {0}.".format(news_file))
        else:
            news_file = NamedTemporaryFile(suffix=".png", delete=False)

            logging.info("Генерируется изображение текущих новостей.")
            logging.debug("Изображение новостей сохраняется во временный файл: {0}.".format(
                news_file.name)
            )

            image = Image.new("RGBA", (2560, 10240), (35, 35, 35))
            draw = ImageDraw.Draw(image)

            # Необходимые переменные: даты последнего обновления, шаблон текста для обновления, шрифты
            br_news_date = utils.convert_to_moscow(utils.convert_iso_time(news_json['battleroyale']['last_modified']))
            pve_news_date = utils.convert_to_moscow(utils.convert_iso_time(news_json['savetheworld']['last_modified']))
            category_last_update_date_text = "Последнее обновление новостей {0} произошло {1} в {2} по московскому времени"
            font_news_header = ImageFont.truetype("assets/fonts/Montserrat-Black.ttf", 144)
            font_news_categories = ImageFont.truetype("assets/fonts/Montserrat-Black.ttf", 72)
            font_news_ext = ImageFont.truetype("assets/fonts/RobotoCondensed-Regular.ttf", 48)
            font_news_item_header = ImageFont.truetype("assets/fonts/Montserrat-Bold.ttf", 64)
            font_news_item_body = ImageFont.truetype("assets/fonts/RobotoCondensed-Bold.ttf", 48)

            draw.text(xy=(100, 150), text="Новости в Фортнайте".upper(), fill=(255, 255, 255), font=font_news_header)

            # Пишем заголовки для Королевской Битвы: Королевская Битва, дата последнего обновления новостей
            draw.text(xy=(100, 450), text="Королевская Битва", fill=(255, 255, 255), font=font_news_categories)
            draw.text(xy=(100, 550), text=category_last_update_date_text.format(
                "Королевской Битвы", br_news_date.strftime("%d.%m.%Y"), br_news_date.strftime("%H:%M")
            ), fill=(173, 173, 173), font=font_news_ext)

            last_news_item_position = [100, 700]
            for br_news_item in news_json['battleroyale']['news']:
                try:
                    news_item_file = NamedTemporaryFile(suffix=".png")
                    news_item_file.write(requests.get(br_news_item['image']).content)

                    news_item_image = Image.open(news_item_file.name)
                    news_item_image.thumbnail((1024, 512), Image.ANTIALIAS)

                    draw.rectangle(((1134, last_news_item_position[1]), (2460, last_news_item_position[1] + 521)),
                                   width=5, outline=(255, 255, 255), fill=(50, 50, 50))
                    news_item_image = ImageOps.expand(news_item_image, border=5, fill=(255, 255, 255))
                    image.paste(news_item_image, tuple(last_news_item_position))

                    draw.text(xy=(last_news_item_position[0] + 1060, last_news_item_position[1] + 10),
                              text=br_news_item['title'], fill=(255, 255, 255), font=font_news_item_header)
                    # draw.multiline_text(xy=(last_news_item_position[0] + 1050, last_news_item_position[1] + 40),
                    #                     text=br_news_item['body'], fill=(255, 255, 255), font=font_news_categories,
                    #                     align="left")

                    last_news_item_position = [last_news_item_position[0], last_news_item_position[1] + 600]
                except:
                    logging.error("Произошла ошибка при парсировании новости.", exc_info=True)
                    continue

            # Пишем заголовки для Сражения с Бурей: Сражение с Бурей, дата последнего обновления новостей
            draw.text(xy=(100, last_news_item_position[1] + 150), text="Сражение с Бурей", fill=(255, 255, 255),
                      font=font_news_categories)
            draw.text(xy=(100, last_news_item_position[1] + 250), text=category_last_update_date_text.format(
                "Сражения с Бурей", pve_news_date.strftime("%d.%m.%Y"), pve_news_date.strftime("%H:%M")
            ), fill=(173, 173, 173), font=font_news_ext)
            last_news_item_position = [last_news_item_position[0], last_news_item_position[1] + 250]

            image = image.crop((0, 0, 2560, last_news_item_position[1] + 600))
            image.save(news_file.name)

            news_file = news_file.name
            await Redis.execute("SET", "fortnite:news:file:{0}".format(news_hash), news_file, "EX", 86400)

        return news_file, news_hash
    except Exception:
        logging.error("Произошла ошибка при генерации изображения текущих новостей в Фортнайте.", exc_info=True)
        return "Произошла ошибка при генерации изображения текущих новостей в Фортнайте."

if __name__ == "__main__":
    try:
        asyncio.get_event_loop().run_until_complete(news())
    except KeyboardInterrupt:
        pass
