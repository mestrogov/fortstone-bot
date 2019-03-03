# -*- coding: utf-8 -*-

from app import logging
from app.remote.redis import Redis
from app.api.utils import colors
from tempfile import NamedTemporaryFile
from PIL import Image, ImageDraw, ImageFont, ImageOps
import logging
import json
import math
import requests
import asyncio


async def store():
    try:
        api_store_url = "https://fortnite-public-api.theapinetwork.com/prod09/store/get?language=en"

        store_json = requests.get(api_store_url).json()
        # Создаем временный файл для итоговой фотографии магазина, которая уже непосредственно будет загружена
        with NamedTemporaryFile(suffix=".jpg") as store_file:
            for item in store_json['items']:
                item_file = NamedTemporaryFile(suffix=".png", delete=False)

                logging.info("Генерируется фотография для предмета {0}.".format(item['name']))
                logging.debug("Сохраняется фотография во временный файл: {0}".format(item_file.name))

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
    except Exception:
        logging.error("Произошла ошибка при попытке парсирования ежедневного магазина Fortnite.", exc_info=True)
        return "Произошла ошибка при попытке получения ежедневного магазина Fortnite."

if __name__ == "__main__":
    try:
        asyncio.get_event_loop().run_until_complete(store())
    except KeyboardInterrupt:
        pass
