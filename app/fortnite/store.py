# -*- coding: utf-8 -*-

from app import logging
from app import config
from app import utils
from app.remote.redis import Redis
from app.fortnite.utils import store_colors
from tempfile import NamedTemporaryFile
from PIL import Image, ImageDraw, ImageFont, ImageOps
from secrets import token_hex
from hashlib import sha1
from os.path import isfile
import json
import logging
import math
import requests
import asyncio


async def item_parse(item, featured=False):
    item_file = NamedTemporaryFile(suffix=".png", delete=False)
    logging.debug("Фотография предмета сохраняется во временный файл: {0}".format(item_file.name))

    # Обозначает полноту изображения предмета (т.е. например: есть или нет иконки)
    error_status = False
    image = Image.new("RGBA", (512, 512), (255, 0, 0))

    try:
        # Если изображения предмета пока что нет, то выдает ссылку на эти изображения
        unknown_placeholders = ["https://image.fnbr.co/misc/placeholder.png", "https://image.fnbr.co/misc/question.png"]
        if item['images']['icon'] in unknown_placeholders:
            logging.info("У предмета нет иконки, поэтому следует немного подождать, пока она будет добавлена в API.")
            error_status = True

            # Вызываем Exception, чтобы получить иконку предмета
            raise Exception
        elif featured and item['images']['featured']:
            item_file.write(requests.get(item['images']['featured']).content)
        else:
            raise Exception
    except:
        item_file.write(requests.get(item['images']['icon']).content)

    # Делаем задний фон в зависимости от редкости
    # Оригинал: https://stackoverflow.com/a/30669765
    center_color = store_colors.get_frame_center_color(item['rarity'])
    corner_color = store_colors.get_frame_corner_color(item['rarity'])
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

    # Делаем полупрозрачное выделение для названия и цены предмета
    s_image = Image.new("RGBA", (512, 512), (255, 0, 0, 0))
    s_image_draw = ImageDraw.Draw(s_image)
    s_image_draw.rectangle(((0, 512), (512, 400)), fill=(0, 0, 0, 110))
    image = Image.alpha_composite(image, s_image)

    # Необходимые переменные: название, цена предмета, шрифты
    item_name = item['name'].upper()
    item_cost = item['price']
    # Формула для вычисления необходимого размера шрифта: чем длиннее название, тем меньше шрифт
    font_name_size = int(56 - 0.85 * (len(item_name)))
    font_name = ImageFont.truetype("assets/fonts/Montserrat-ExtraBold.ttf", font_name_size)
    font_cost = ImageFont.truetype("assets/fonts/Montserrat-Bold.ttf", 48)

    # Получаем ширину, высоту названия и цены предмета
    draw = ImageDraw.Draw(image)
    item_name_width, item_image_height = draw.textsize(item_name, font=font_name)
    item_cost_width, item_cost_height = draw.textsize(item_cost, font=font_cost)

    # Пишем название предмета на изображении
    draw.text(xy=((512 - item_name_width) // 2, 400),
              text=item_name, fill=(255, 255, 255), font=font_name)

    # Вставляем иконку В-Баксов
    vbucks_image = Image.open("assets/icons/vbucks.png")
    vbucks_image.thumbnail((50, 50), Image.ANTIALIAS)
    image.paste(vbucks_image, ((460 - item_cost_width) // 2, 455), vbucks_image)

    # Пишем цену предмета
    draw.text(xy=((570 - item_cost_width) // 2, 450),
              text=item_cost, fil=(255, 255, 255), font=font_cost)

    # Делаем рамку в зависимости от редкости
    image = ImageOps.expand(image, border=5, fill=store_colors.get_frame_border_color(item['rarity']))

    image.save(item_file.name, "PNG")
    return item_file.name, error_status


async def store(ignore_cache=False):
    try:
        if ignore_cache:
            logging.info("Изображение текущего магазина запрошено с игнорированием кэша.")

        api_store_url = "https://fnbr.co/api/shop"
        store_json = (await Redis.execute("GET", "fortnite:store:json"))['details']
        if store_json and not ignore_cache:
            store_json = json.loads(store_json)
        else:
            store_json = requests.get(api_store_url, headers={"x-api-key": config.FNBR_API_KEY}).json()
            await Redis.execute("SET", "fortnite:store:json", json.dumps(store_json), "EX", 25)

        if not store_json['status'] == 200:
            logging.error("Произошла ошибка при получении текущего магазина. API вернуло неуспешный статус. {0}".format(
                store_json)
            )
            return
        else:
            store_json = store_json['data']

        store_hash = sha1(str(store_json['date']).encode("UTF-8")).hexdigest()
        # Переменная, отвечающая за "правильность" генерации магазина. Если она равна False, то изображение кэшироваться
        # не будет, а хэш магазина всегда будет рандомный, тем самым предовращает кэширование где-либо
        shop_generated_successfully = True

        store_file = (await Redis.execute("GET", "fortnite:store:file:{0}".format(store_hash)))['details']
        if store_file and isfile(store_file) and not ignore_cache:
            logging.info("Изображение текущего магазина уже сгенерировано, файл: {0}.".format(store_file))
        else:
            store_file = NamedTemporaryFile(suffix=".png", delete=False)

            logging.info("Генерируется изображение магазина от {0}.".format(
                utils.convert_to_moscow(utils.convert_iso_time(store_json['date'])).strftime("%d.%m.%Y"))
            )
            logging.debug("Изображение магазина сохраняется во временный файл: {0}.".format(store_file.name))

            image = Image.new("RGBA", (2700, 10240), (35, 35, 35))
            draw = ImageDraw.Draw(image)

            # Переменные для изменения текста на изображении
            shop_date = utils.convert_to_moscow(utils.convert_iso_time(store_json['date']))
            shop_text = "Магазин предметов".upper()
            shop_ext = "Обновление магазина предметов произошло {0} в {1} по московскому времени.".format(
                shop_date.strftime("%d.%m.%Y"), shop_date.strftime("%H:%M")
            )
            # Технические переменные: шрифты
            font_shop_text = ImageFont.truetype("assets/fonts/Montserrat-Black.ttf", 80)
            font_shop_ext = ImageFont.truetype("assets/fonts/Roboto-Regular.ttf", 56)
            font_shop_category_names = ImageFont.truetype("assets/fonts/Montserrat-ExtraBold.ttf", 72)

            # Пишем заголовок магазина (например: Магазин в Фортнайте) и дополнительную информацию
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
            for num, featured_item_json in enumerate(store_json['featured'], 1):
                try:
                    featured_item_image, error_status = await item_parse(featured_item_json, featured=True)
                    if error_status:
                        shop_generated_successfully = False

                    if num == 1:
                        image.paste(Image.open(featured_item_image), tuple(last_featured_item_location))
                    elif num % 2 == 0:
                        last_featured_item_location[0] = last_featured_item_location[0] + 600
                        image.paste(Image.open(featured_item_image), tuple(last_featured_item_location))
                    else:
                        last_featured_item_location = [last_featured_item_location[0] - 600, last_featured_item_location[1] + 600]
                        image.paste(Image.open(featured_item_image), tuple(last_featured_item_location))
                except:
                    logging.error("Произошла ошибка при вставке/генерации изображения рекомендуемого предмета.",
                                  exc_info=True)
                    continue

            # Вставляем изображения ежедневных предметов
            last_daily_item_location = [1500, 468]
            for num, daily_item_json in enumerate(store_json['daily'], 1):
                try:
                    daily_item, error_status = await item_parse(daily_item_json)
                    if error_status:
                        shop_generated_successfully = False

                    if num == 1:
                        image.paste(Image.open(daily_item), tuple(last_daily_item_location))
                    elif num % 2 == 0:
                        last_daily_item_location[0] = last_daily_item_location[0] + 600
                        image.paste(Image.open(daily_item), tuple(last_daily_item_location))
                    else:
                        last_daily_item_location = [last_daily_item_location[0] - 600, last_daily_item_location[1] + 600]
                        image.paste(Image.open(daily_item), tuple(last_daily_item_location))
                except:
                    logging.error("Произошла ошибка при вставке/генерации изображения ежедневного предмета.",
                                  exc_info=True)
                    continue

            # Обрезаем изображение до необходимых размеров
            shop_category_widths = [last_featured_item_location[1], last_daily_item_location[1]]
            image = image.crop((0, 0, 2700, max(shop_category_widths) + 600))

            image.save(store_file.name, "PNG")
            store_file = store_file.name
            # Проверяем, сгенерирован ли правильно/полностью магазин предметов. Если нет, то не кэшируем
            # файл изображения
            if shop_generated_successfully:
                await Redis.execute("SET", "fortnite:store:file:{0}".format(store_hash), store_file, "EX", 86400)

        # Проверяем, сгенерирован ли правильно/полностью магазин предметов. Если нет, то возвращаем рандомный hash,
        # чтобы предотвратить любое кэширование
        if shop_generated_successfully:
            return store_file, store_hash
        else:
            logging.info("Изображение магазина предметов был сгенерирован неполностью, поэтому хэш магазина рандомный.")
            return store_file, token_hex(16)
    except Exception:
        logging.error("Произошла ошибка при генерации изображения магазина.", exc_info=True)
        return "Произошла ошибка при генерации изображения магазина."

if __name__ == "__main__":
    try:
        asyncio.get_event_loop().run_until_complete(store(ignore_cache=True))
    except KeyboardInterrupt:
        pass
