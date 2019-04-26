# -*- coding: utf-8 -*-

from app import logging
from app.remote.redis import Redis
from app.fortnite.utils.multiline_text_wrap import wrap
from app import utils
from tempfile import NamedTemporaryFile
from PIL import Image, ImageDraw, ImageFont, ImageOps
from hashlib import sha1
from os.path import isfile
import json
import logging
import requests
import asyncio


def parse_ingame_news():
    news_api_url = "https://fortnitecontent-website-prod07.ol.epicgames.com/content/api/pages/fortnite-game"
    response = requests.get(news_api_url, headers={"Accept-Language": "ru"}).json()

    # Парсирование экстренных сообщений для Королевской Битвы и Сражения с Бурей
    for notice_message in response['emergencynotice']['news']['messages']:
        notice = {
            "image": "https://i.imgur.com/9nGBW3U.jpg",
            "adspace": "ЭКСТРЕННОЕ СООБЩЕНИЕ!",
            "title": notice_message['title'],
            "body": notice_message['body'],
        }
        try:
            assert notice_message['subgame']
            response['savetheworldnews']['news']['messages'].insert(0, notice)
        except (AssertionError, KeyError, TypeError):
            response['battleroyalenews']['news']['messages'].insert(0, notice)

    ingame_news = {
        "emergencynotice": {
            "last_modified": response['emergencynotice']['lastModified'],
        },
        "battleroyale": {
            "last_modified": response['battleroyalenews']['lastModified'],
            "locale": response['battleroyalenews']['_locale'],
            "news": response['battleroyalenews']['news']['messages']
        },
        "savetheworld": {
            "last_modified": response['savetheworldnews']['lastModified'],
            "locale": response['savetheworldnews']['_locale'],
            "news": response['savetheworldnews']['news']['messages']
        }
    }

    return ingame_news


async def news_item_parse(news_item, font_title, font_body):
    news_item_file = NamedTemporaryFile(suffix=".png", delete=False)
    news_item_file.write(requests.get(news_item['image']).content)
    logging.debug("Изображение элемента из текущих новостей сохраняется в файл: {0}.".format(news_item_file.name))

    image = Image.new("RGBA", (2360, 522), (255, 0, 0))
    draw = ImageDraw.Draw(image)

    # Проверка наличия места для рекламы (adspace)
    try:
        adspace = news_item['adspace']
    except KeyError:
        adspace = None

    # Вставляем изображение новости и рисуем рамку
    news_item_image = Image.open(news_item_file.name)
    news_item_image.thumbnail((1024, 512), Image.ANTIALIAS)
    news_item_image = ImageOps.expand(news_item_image, border=5, fill=(255, 255, 255))
    image.paste(news_item_image, (0, 0))

    # Рисуем рамку для новости и выделяем цветом место текста (тела и заголовка) новости
    draw.rectangle(((1029, 0), (2359, 521)),
                   width=5, outline=(255, 255, 255), fill=(50, 50, 50))
    # Выделяем цветом название новости
    draw.rectangle(((1034, 5), (2354, 106)), fill=(25, 25, 38))

    # Пишем название новости
    draw.text(xy=(1064, 15), text=news_item['title'], fill=(255, 255, 255), font=font_title)
    # Пишем текст (тело) новости с ограничением строки до 1.000 пикселей
    draw.multiline_text(xy=(1066, 123), text=wrap(news_item['body'], font_body, 1000),
                        fill=(255, 255, 255), font=font_body, align="left")

    image.save(news_item_file.name, "PNG")
    return news_item_file.name


async def news(ignore_cache=False):
    try:
        if ignore_cache:
            logging.info("Изображение текущих новостей запрошено с игнорированием кэша.")

        news_json = (await Redis.execute("GET", "fortnite:news:json"))['details']
        if news_json and not ignore_cache:
            news_json = json.loads(news_json)
        else:
            news_json = parse_ingame_news()
            await Redis.execute("SET", "fortnite:news:json", json.dumps(news_json), "EX", 25)

        news_hash = sha1(str(
            news_json['battleroyale']['last_modified'] + news_json['savetheworld']['last_modified'] +
            news_json['emergencynotice']['last_modified']
        ).encode("UTF-8")).hexdigest()

        news_file = (await Redis.execute("GET", "fortnite:news:file:{0}".format(news_hash)))['details']
        if news_file and isfile(news_file) and not ignore_cache:
            logging.info("Изображение текущих новостей уже сгенерировано, файл: {0}.".format(news_file))
        else:
            news_file = NamedTemporaryFile(suffix=".png", delete=False)

            logging.info("Генерируется изображение текущих новостей.")
            logging.debug("Изображение новостей сохраняется во временный файл: {0}.".format(news_file.name))

            image = Image.new("RGBA", (5120, 10240), (35, 35, 35))
            draw = ImageDraw.Draw(image)

            # Переменные для изменения текста на изображении
            news_header_text = "Внутриигровые новости в Фортнайте".upper()
            news_ext_text = "Больше новостей в нашей группе ВКонтакте или канале Telegram"
            category_last_update_date_text = "Обновление новостей {0} произошло {1} в {2} по московскому времени"
            # Технические переменные: шрифты, время
            br_news_date = utils.convert_to_moscow(utils.convert_iso_time(news_json['battleroyale']['last_modified']))
            pve_news_date = utils.convert_to_moscow(utils.convert_iso_time(news_json['savetheworld']['last_modified']))
            font_news_header = ImageFont.truetype("assets/fonts/Montserrat-Black.ttf", 80)
            font_news_ext = ImageFont.truetype("assets/fonts/Roboto-Regular.ttf", 48)
            font_news_categories = ImageFont.truetype("assets/fonts/Montserrat-ExtraBold.ttf", 72)
            font_news_item_title = ImageFont.truetype("assets/fonts/Montserrat-Bold.ttf", 58)
            font_news_item_body = ImageFont.truetype("assets/fonts/Roboto-Regular.ttf", 48)

            # Пишем заголовок новостей (например: Новости в Фортнайте) и дополнительную информацию
            news_header_width, news_header_height = draw.textsize(news_header_text, font=font_news_header)
            news_ext_width, news_ext_height = draw.textsize(news_ext_text, font=font_news_ext)
            draw.text(xy=((5120 - news_header_width) // 2, 20), text=news_header_text, fill=(255, 255, 255),
                      font=font_news_header)
            draw.text(xy=((5120 - news_ext_width) // 2, 120), text=news_ext_text, fill=(173, 173, 173),
                      font=font_news_ext)

            # Пишем заголовки для Королевской Битвы: Королевская Битва, дата последнего обновления новостей
            draw.text(xy=(100, 300), text="Королевская Битва", fill=(255, 255, 255), font=font_news_categories)
            draw.text(xy=(100, 380), text=category_last_update_date_text.format(
                "Королевской Битвы", br_news_date.strftime("%d.%m.%Y"), br_news_date.strftime("%H:%M")
            ), fill=(173, 173, 173), font=font_news_ext)

            # Переменная для обозначения координат места, куда будет помещена новость
            br_last_news_item_position = [100, 525]
            # Вставляем изображение каждой новости Королевской Битвы
            for br_news_item in news_json['battleroyale']['news']:
                try:
                    br_news_item_file = await news_item_parse(br_news_item, font_news_item_title, font_news_item_body)
                    image.paste(Image.open(br_news_item_file), tuple(br_last_news_item_position))
                    br_last_news_item_position = [br_last_news_item_position[0], br_last_news_item_position[1] + 622]
                except:
                    logging.error("Произошла ошибка при парсировании элемента новостей Королевской Битвы.",
                                  exc_info=True)
                    continue

            # Пишем заголовки для Сражения с Бурей: Сражение с Бурей, дата последнего обновления новостей
            draw.text(xy=(2660, 300), text="Сражение с Бурей", fill=(255, 255, 255),
                      font=font_news_categories)
            draw.text(xy=(2660, 380), text=category_last_update_date_text.format(
                "Сражения с Бурей", pve_news_date.strftime("%d.%m.%Y"), pve_news_date.strftime("%H:%M")
            ), fill=(173, 173, 173), font=font_news_ext)

            # Переменная для обозначения координат места, куда будет помещена новость
            pve_last_news_item_position = [2660, 525]
            # Вставляем изображение каждой новости Сражения с Бурей
            for pve_news_item in news_json['savetheworld']['news']:
                try:
                    pve_news_item_file = await news_item_parse(pve_news_item, font_news_item_title, font_news_item_body)
                    image.paste(Image.open(pve_news_item_file), tuple(pve_last_news_item_position))
                    pve_last_news_item_position = [pve_last_news_item_position[0], pve_last_news_item_position[1] + 622]
                except:
                    logging.error("Произошла ошибка при парсировании элемента новостей Сражения с Бурей.",
                                  exc_info=True)
                    continue

            image = image.crop((0, 0, 5120, max([br_last_news_item_position[1], pve_last_news_item_position[1]])))
            image.save(news_file.name, "PNG")

            news_file = news_file.name
            await Redis.execute("SET", "fortnite:news:file:{0}".format(news_hash), news_file, "EX", 86400)

        return news_file, news_hash
    except Exception:
        logging.error("Произошла ошибка при генерации изображения текущих новостей в Фортнайте.", exc_info=True)
        return "Произошла ошибка при генерации изображения текущих новостей в Фортнайте."

if __name__ == "__main__":
    try:
        asyncio.get_event_loop().run_until_complete(news(ignore_cache=True))
    except KeyboardInterrupt:
        pass
