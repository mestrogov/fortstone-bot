# -*- coding: utf-8 -*-

from app import logging
from app.remote.redis import Redis
from app.fortnite.parser.utils import store_colors
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


async def store(ignore_cache=False):
    try:
        if ignore_cache:
            logging.info("Изображение текущего магазина предметов запрошено с игнорированием кэша.")

        api_store_url = "https://fortnite-public-api.theapinetwork.com/prod09/store/get?language=en"
        store_json = (await Redis.execute("GET", "fortnite:store:json"))['details']
        if store_json and not ignore_cache:
            store_json = json.loads(store_json)
        else:
            store_json = requests.get(api_store_url).json()
            await Redis.execute("SET", "fortnite:store:json", json.dumps(store_json), "EX", 20)

        store_hash = sha1(str(store_json['lastupdate']).encode("UTF-8")).hexdigest()

        store_file = (await Redis.execute("GET", "fortnite:store:file:{0}".format(store_hash)))['details']
        if store_file and isfile(store_file) and not ignore_cache:
            logging.info("Изображение текущего магазина предметов уже сгенерировано, файл: {0}.".format(store_file))
        else:
            store_file = NamedTemporaryFile(suffix=".png", delete=False)
            featured_items_files = []
            daily_items_files = []

            logging.info("Генерируется изображение магазина от {0}.".format(store_json['date']))

            for item in store_json['items']:
                try:
                    item_file = NamedTemporaryFile(suffix=".png", delete=False)

                    logging.info("Генерируется фотография для предмета {0}.".format(item['name']))
                    logging.debug("Фотография предмета сохраняется во временный файл: {0}".format(item_file.name))

                    # Если предмет находится в категории "Рекомендуемое", то скачиваем фотографию в полный рост
                    try:
                        if item['featured']:
                            item_file.write(requests.get(item['item']['images']['featured']['transparent']).content)
                        else:
                            raise Exception
                    except:
                        item_file.write(requests.get(item['item']['images']['transparent']).content)

                    image = Image.new("RGBA", (512, 512), (255, 0, 0))

                    # Делаем задний фон в зависимости от редкости
                    # Оригинал: https://stackoverflow.com/a/30669765
                    center_color = store_colors.get_frame_center_color(item['item']['rarity'])
                    corner_color = store_colors.get_frame_corner_color(item['item']['rarity'])
                    for y in range(512):
                        for x in range(512):
                            distance_to_center = math.sqrt((x - 512 / 2) ** 2 + (y - 512 / 2) ** 2)
                            distance_to_center = float(distance_to_center) / (math.sqrt(2) * 512 / 2)

                            r = corner_color[0] * distance_to_center + center_color[0] * (1 - distance_to_center)
                            g = corner_color[1] * distance_to_center + center_color[1] * (1 - distance_to_center)
                            b = corner_color[2] * distance_to_center + center_color[2] * (1 - distance_to_center)

                            image.putpixel((x, y), (int(r), int(g), int(b)))

                    # Вставляем фотографию предмета по по центру на уже готовый задний фон
                    # Оригинал: https://stackoverflow.com/a/2563883
                    item_image = Image.open(item_file.name).convert("RGBA")
                    item_image.thumbnail((512, 512), Image.ANTIALIAS)
                    item_image_width, item_image_height = item_image.size
                    background_image_width, background_image_height = image.size
                    offset = ((background_image_width - item_image_width) // 2,
                              (background_image_height - item_image_height) // 2)
                    image.paste(item_image, offset, item_image)

                    # Делаем полупрозрачное выделение для названия предмета
                    s_image = Image.new("RGBA", (512, 512), (255, 0, 0, 0))
                    s_image_draw = ImageDraw.Draw(s_image)
                    s_image_draw.rectangle(((0, 512 - 50), (512, 512 - 117)), fill=(0, 0, 0, 110))
                    image = Image.alpha_composite(image, s_image)

                    # Необходимые переменные: название, цена предмета, шрифты
                    item_name = item['name'].upper()
                    item_cost = "{:,}".format(int(item['cost']))
                    # Формула для вычисления необходимого размера шрифта: чем длиннее название, тем меньше шрифт
                    font_name_size = int(72 - 0.75 * (len(item_name)))
                    font_name = ImageFont.truetype("assets/fonts/BurbankBigCondensed-Bold.otf", font_name_size)
                    font_cost = ImageFont.truetype("assets/fonts/BurbankBigCondensed-Bold.otf", 42)

                    # Получаем ширину, высоту названия и цены предмета
                    draw = ImageDraw.Draw(image)
                    item_name_width, item_image_height = draw.textsize(item_name, font=font_name)
                    item_cost_width, item_cost_height = draw.textsize(item_cost, font=font_cost)

                    # Пишем название предмета на изображении
                    draw.text(xy=((512 - item_name_width) // 2, 512 - 110),
                              text=item_name, fill=(255, 255, 255), font=font_name)

                    # Делаем выделение текста для цены
                    draw.rectangle(((0, 512), (512, 512 - 50)), fill=(7, 0, 35))

                    # Вставляем иконку В-Баксов
                    vbucks_image = Image.open("assets/icons/vbucks.png")
                    vbucks_image.thumbnail((42, 42), Image.ANTIALIAS)
                    image.paste(vbucks_image, ((512 - item_cost_width - 55) // 2, 512 - 46), vbucks_image)

                    # Пишем цену предмета
                    draw.text(xy=((512 - item_cost_width + 41) // 2, 512 - 42),
                              text=item_cost, fil=(255, 255, 255), font=font_cost)

                    # Делаем рамку в зависимости от редкости
                    image = ImageOps.expand(image, border=5, fill=store_colors.get_frame_border_color(item['item']['rarity']))

                    image.save(item_file.name, "PNG")
                    if item['featured']:
                        featured_items_files.extend([item_file.name])
                    else:
                        daily_items_files.extend([item_file.name])
                except:
                    logging.error("Произошла ошибка при генерировании фотографии для предмета {0}.".format(item['name']),
                                  exc_info=True)
                    continue

            logging.debug("Изображение магазина предметов сохраняется во временный файл: {0}.".format(store_file.name))

            image = Image.new("RGBA", (2700, 10240), (35, 35, 35))
            draw = ImageDraw.Draw(image)

            # Необходимые переменные: описание магазина предметов (дата, подробности), шрифты
            shop_date = pytz.utc.localize(datetime.datetime.strptime(store_json['date'], "%d-%m-%y")).astimezone(
                pytz.timezone("Europe/Moscow"))
            shop_text = "Магазин предметов в Фортнайте".upper()
            shop_ext = "{0} | https://t.me/fortnitearchives".format(shop_date.strftime("%d.%m.%Y"))
            font_shop_text = ImageFont.truetype("assets/fonts/Montserrat-Black.ttf", 80)
            font_shop_ext = ImageFont.truetype("assets/fonts/Roboto-Regular.ttf", 56)
            font_shop_category_names = ImageFont.truetype("assets/fonts/Montserrat-ExtraBold.ttf", 72)

            # Пишем дату магазина предметов и дополнительный текст (подробности)
            shop_text_width, shop_text_height = draw.textsize(shop_text, font=font_shop_text)
            shop_ext_width, shop_ext_height = draw.textsize(shop_ext, font=font_shop_ext)
            draw.text(xy=((2700 - shop_text_width) // 2, 20), text=shop_text,
                      fill=(255, 255, 255), font=font_shop_text)
            draw.text(xy=((2700 - shop_ext_width) // 2, 120), text=shop_ext,
                      fill=(173, 173, 173), font=font_shop_ext)

            # Пишем название категорий (рекомендуемое, ежедневное)
            shop_category_featured_width, shop_category_featured_height = draw.textsize("Рекомендуемые".upper(),
                                                                                        font_shop_category_names)
            shop_category_daily_width, shop_category_daily_height = draw.textsize("Ежедневные".upper(),
                                                                                  font_shop_category_names)
            draw.text(xy=(78 + (1122 - shop_category_featured_width) // 2, 320), text="Рекомендуемые".upper(),
                      fill=(255, 255, 255), font=font_shop_category_names)
            draw.text(xy=(1500 + (1122 - shop_category_daily_width) // 2, 320), text="Ежедневные".upper(),
                      fill=(255, 255, 255), font=font_shop_category_names)

            # Вставляем изображения рекомендуемых предметов
            last_featured_item_location = [78, 468]
            for num, featured_item_file in enumerate(featured_items_files, 1):
                featured_item = Image.open(featured_item_file)
                if num == 1:
                    image.paste(featured_item, tuple(last_featured_item_location))
                elif num % 2 == 0:
                    last_featured_item_location[0] = last_featured_item_location[0] + 600
                    image.paste(featured_item, tuple(last_featured_item_location))
                else:
                    last_featured_item_location = [last_featured_item_location[0] - 600, last_featured_item_location[1] + 600]
                    image.paste(featured_item, tuple(last_featured_item_location))

            # Вставляем изображения ежедневных предметов
            last_daily_item_location = [1500, 468]
            for num, daily_item_file in enumerate(daily_items_files, 1):
                daily_item = Image.open(daily_item_file)
                if num == 1:
                    image.paste(daily_item, tuple(last_daily_item_location))
                elif num % 2 == 0:
                    last_daily_item_location[0] = last_daily_item_location[0] + 600
                    image.paste(daily_item, tuple(last_daily_item_location))
                else:
                    last_daily_item_location = [last_daily_item_location[0] - 600, last_daily_item_location[1] + 600]
                    image.paste(daily_item, tuple(last_daily_item_location))

            # Обрезаем изображение до необходимых размеров
            shop_category_widths = [last_featured_item_location[1], last_daily_item_location[1]]
            image = image.crop((0, 0, 2700, max(shop_category_widths) + 600))

            image.save(store_file.name, "PNG")
            store_file = store_file.name
            await Redis.execute("SET", "fortnite:store:file:{0}".format(store_hash), store_file, "EX", 86400)

        return store_file, store_hash
    except Exception:
        logging.error("Произошла ошибка при генерации изображения магазина предметов в Фортнайте.", exc_info=True)
        return "Произошла ошибка при генерации изображения магазина предметов в Фортнайте."

if __name__ == "__main__":
    try:
        asyncio.get_event_loop().run_until_complete(store(ignore_cache=True))
    except KeyboardInterrupt:
        pass
