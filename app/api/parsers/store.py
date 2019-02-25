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
                with NamedTemporaryFile(suffix=".png", delete=False) as item_file:
                    logging.debug("Сохраняется фотография предмета во временный файл: {0}".format(item_file.name))
                    # Скачиваем фотографию предмета без названия и цены
                    logging.debug("Рекомендуемый ли предмет: {0}".format(item['featured']))
                    try:
                        item_file.write(requests.get(item['item']['images']['featured']['transparent']).content)
                    except requests.exceptions.MissingSchema:
                        item_file.write(requests.get(item['item']['images']['transparent']).content)

                    image = Image.new("RGBA", (256, 256), (255, 0, 0, 0))

                    # Делаем задний фон в зависимости от редкости; оригинал: https://stackoverflow.com/a/30669765
                    center_color = colors.get_frame_center_color(item['item']['rarity'])
                    corner_color = colors.get_frame_corner_color(item['item']['rarity'])
                    for y in range(256):
                        for x in range(256):
                            distance_to_center = math.sqrt((x - 256 / 2) ** 2 + (y - 256 / 2) ** 2)
                            # Make it on a scale from 0 to 1
                            distance_to_center = float(distance_to_center) / (math.sqrt(2) * 256 / 2)

                            # Calculate r, g, and b values
                            r = corner_color[0] * distance_to_center + center_color[0] * (1 - distance_to_center)
                            g = corner_color[1] * distance_to_center + center_color[1] * (1 - distance_to_center)
                            b = corner_color[2] * distance_to_center + center_color[2] * (1 - distance_to_center)

                            # Place the pixel
                            image.putpixel((x, y), (int(r), int(g), int(b)))

                    # Уменьшаем фотографию, чтобы она помещалась в рамку
                    pass

                    # Вставляем фотографию предмета поверх уже готового заднего фона
                    item_image = Image.open(item_file.name)
                    item_image_width, item_image_height = item_image.size
                    background_image_width, background_image_height = image.size
                    offset = ((background_image_width - item_image_width) // 2,
                              (background_image_height - item_image_height) // 2)
                    image.paste(item_image, offset, item_image)

                    # Делаем рамку в зависимости от редкости
                    image = ImageOps.expand(image, border=3, fill=colors.get_frame_border_color(item['item']['rarity']))
                    # font = ImageFont.truetype("assets/fonts/BurbankBigCondensed-Bold.otf", 72)
                    # draw = ImageDraw.Draw(image)
                    # draw.text(xy=(100, 200), text=item['name'].upper(), fill="white", font=font)
                    image.save(item_file.name, "PNG")
    except Exception as e:
        logging.error("Произошла ошибка при выполнении команды /store.", exc_info=True)
        return "Произошла ошибка при попытке получения ежедневного магазина Fortnite."

if __name__ == "__main__":
    try:
        asyncio.get_event_loop().run_until_complete(store())
    except KeyboardInterrupt:
        pass
