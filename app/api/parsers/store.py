# -*- coding: utf-8 -*-

from app import logging
from app.remote.redis import Redis
from app.api.utils import colors
from tempfile import NamedTemporaryFile
from PIL import Image, ImageDraw, ImageFont, ImageOps
import pytz
import datetime
import logging
import json
import math
import requests
import asyncio


async def store():
    try:
        api_store_url = "https://fortnite-public-api.theapinetwork.com/prod09/store/get?language=en"

        store_json = requests.get(api_store_url).json()
        # store_json = {"date_layout":"day-month-year","lastupdate":1551571214,"language":"en","date":"03-03-19","rows":13,"vbucks":"https://fortnite-public-files.theapinetwork.com/fortnite-vbucks-icon.png","items":[{"itemid":"76fe82f-693c99a-d3297b4-bdf9d31","name":"Reflex","cost":"1200","featured":1,"refundable":1,"lastupdate":1551571213,"youtube":None,"item":{"image":"https://fortnite-public-files.theapinetwork.com/outfit/b351f01a4c2701640183c1aa431eb8ba.png","images":{"transparent":"https://fortnite-public-files.theapinetwork.com/outfit/b351f01a4c2701640183c1aa431eb8ba.png","background":"https://fortnite-public-files.theapinetwork.com/image/76fe82f-693c99a-d3297b4-bdf9d31.png","information":"https://fortnite-public-files.theapinetwork.com/image/76fe82f-693c99a-d3297b4-bdf9d31/item.png","featured":{"transparent":"https://fortnite-public-files.theapinetwork.com/featured/76fe82f-693c99a-d3297b4-bdf9d31.png"}},"captial":"outfit","type":"outfit","rarity":"rare","obtained_type":"vbucks"},"ratings":{"avgStars":3.98,"totalPoints":648,"numberVotes":163}},{"itemid":"43f67c0-cda8fda-0d630f1-ba345d8","name":"Flimsie Flail","cost":"800","featured":1,"refundable":1,"lastupdate":1551571213,"youtube":None,"item":{"image":"https://fortnite-public-files.theapinetwork.com/pickaxe/31fc27b63ca5bf097b9d45ab7c8b63e3.png","images":{"transparent":"https://fortnite-public-files.theapinetwork.com/pickaxe/31fc27b63ca5bf097b9d45ab7c8b63e3.png","background":"https://fortnite-public-files.theapinetwork.com/image/43f67c0-cda8fda-0d630f1-ba345d8.png","information":"https://fortnite-public-files.theapinetwork.com/image/43f67c0-cda8fda-0d630f1-ba345d8/item.png","featured":{"transparent":None}},"captial":"pickaxe","type":"pickaxe","rarity":"rare","obtained_type":"vbucks"},"ratings":{"avgStars":3.97,"totalPoints":850,"numberVotes":214}},{"itemid":"8199036-3210242-6480297-c657fa5","name":"Maverick","cost":"1500","featured":0,"refundable":1,"lastupdate":1551571213,"youtube":None,"item":{"image":"https://fortnite-public-files.theapinetwork.com/outfit/5af0736803f924f768be3f41af7937d6.png","images":{"transparent":"https://fortnite-public-files.theapinetwork.com/outfit/5af0736803f924f768be3f41af7937d6.png","background":"https://fortnite-public-files.theapinetwork.com/image/8199036-3210242-6480297-c657fa5.png","information":"https://fortnite-public-files.theapinetwork.com/image/8199036-3210242-6480297-c657fa5/item.png","featured":{"transparent":"https://fortnite-public-files.theapinetwork.com/featured/8199036-3210242-6480297-c657fa5.png"}},"captial":"outfit","type":"outfit","rarity":"epic","obtained_type":"vbucks"},"ratings":{"avgStars":4.02,"totalPoints":494,"numberVotes":123}},{"itemid":"0896bd2-34ccd96-2cd9ff0-30f47cf","name":"Hyper","cost":"500","featured":0,"refundable":1,"lastupdate":1551571213,"youtube":None,"item":{"image":"https://fortnite-public-files.theapinetwork.com/glider/5ef159e2f3745ee15abe986206a16af6.png","images":{"transparent":"https://fortnite-public-files.theapinetwork.com/glider/5ef159e2f3745ee15abe986206a16af6.png","background":"https://fortnite-public-files.theapinetwork.com/image/0896bd2-34ccd96-2cd9ff0-30f47cf.png","information":"https://fortnite-public-files.theapinetwork.com/image/0896bd2-34ccd96-2cd9ff0-30f47cf/item.png","featured":{"transparent":None}},"captial":"glider","type":"glider","rarity":"uncommon","obtained_type":"vbucks"},"ratings":{"avgStars":3.05,"totalPoints":195,"numberVotes":64}}]}

        store_file = NamedTemporaryFile(suffix=".png", delete=False)
        featured_items_files = []
        daily_items_files = []

        for item in store_json['items']:
            try:
                item_file = NamedTemporaryFile(suffix=".png", delete=False)

                logging.info("Генерируется фотография для предмета {0}.".format(item['name']))
                logging.debug("Фотография предмета сохраняется во временный файл: {0}".format(item_file.name))

                # Сначала пытаемся скачать фотографию предмета в полный рост (featured)
                try:
                    item_file.write(requests.get(item['item']['images']['featured']['transparent']).content)
                except requests.exceptions.MissingSchema:
                    item_file.write(requests.get(item['item']['images']['transparent']).content)

                image = Image.new("RGBA", (512, 512), (255, 0, 0))

                # Делаем задний фон в зависимости от редкости
                # Оригинал: https://stackoverflow.com/a/30669765
                center_color = colors.get_frame_center_color(item['item']['rarity'])
                corner_color = colors.get_frame_corner_color(item['item']['rarity'])
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
                item_image = Image.open(item_file.name)
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
                image = ImageOps.expand(image, border=5, fill=colors.get_frame_border_color(item['item']['rarity']))

                image.save(item_file.name, "PNG")
                if item['featured']:
                    featured_items_files.extend([item_file.name])
                else:
                    daily_items_files.extend([item_file.name])
            except:
                logging.error("Произошла ошибка при генерировании фотографии для предмета {0}.".format(item['name']),
                              exc_info=True)
                continue

        logging.info("Генерируется изображение магазина от {0}.".format(store_json['date']))
        logging.debug("Изображение магазина сохраняется во временный файл: {0}.".format(store_file.name))

        image = Image.new("RGBA", (2560, 10240), (35, 35, 35))
        draw = ImageDraw.Draw(image)

        # Необходимые переменные: шрифты, названия
        shop_date = pytz.utc.localize(datetime.datetime.strptime(store_json['date'], "%d-%m-%y")).astimezone(
            pytz.timezone("Europe/Moscow"))
        shop_info_text = "Ежедневный магазин Fortnite от {0}".format(shop_date.strftime("%d.%m.%Y"))
        shop_copyright_text = "https://t.me/fortnitearchives"
        shop_category_featured = "Рекомендуемые"
        shop_category_daily = "Ежедневные"
        font_shop_info = ImageFont.truetype("assets/fonts/RobotoCondensed-Bold.ttf", 72)
        font_shop_copyright = ImageFont.truetype("assets/fonts/RobotoCondensed-Regular.ttf", 64)
        font_shop_category_names = ImageFont.truetype("assets/fonts/RobotoCondensed-Bold.ttf", 96)

        # Пишем копирайт и дату магазина
        shop_info_width, shop_info_height = draw.textsize(shop_info_text, font=font_shop_info)
        shop_copyright_width, shop_copyright_height = draw.textsize(shop_copyright_text, font=font_shop_copyright)
        draw.text(xy=((2560 - shop_info_width) // 2, 30), text=shop_info_text,
                  fill=(255, 255, 255), font=font_shop_info)
        draw.text(xy=((2560 - shop_copyright_width) // 2, 120), text=shop_copyright_text,
                  fill=(173, 173, 173), font=font_shop_copyright)

        # Пишем название категорий
        shop_category_featured_width, shop_category_featured_height = draw.textsize(shop_category_featured,
                                                                                    font_shop_category_names)
        shop_category_daily_width, shop_category_daily_height = draw.textsize(shop_category_daily,
                                                                              font_shop_category_names)
        draw.text(xy=((1280 - shop_category_featured_width) // 2, 300), text=shop_category_featured,
                  fill=(255, 255, 255), font=font_shop_category_names)
        draw.text(xy=((2560 + shop_category_daily_width) // 2, 300), text=shop_category_daily,
                  fill=(255, 255, 255), font=font_shop_category_names)

        # Вставляем изображения рекомендуемых предметов
        last_featured_item_location = [78, 468]
        last_daily_item_location = (500, 500)

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

        image.save(store_file.name, "PNG")
        return store_file.name
    except Exception:
        logging.error("Произошла ошибка при генерации изображения ежедневного магазина Fortnite.", exc_info=True)
        return "Произошла ошибка при генерации изображения ежедневного магазина Fortnite."

if __name__ == "__main__":
    try:
        asyncio.get_event_loop().run_until_complete(store())
    except KeyboardInterrupt:
        pass
