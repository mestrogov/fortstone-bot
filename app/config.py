# -*- coding: utf-8 -*-

from subprocess import run, PIPE
from os import getenv
from sys import exit
from app.utils import parse_as_boolean
import logging


try:
    # Настройки приложения
    VERSION = str(getenv("VERSION", "Unknown"))
    COMMIT = str(run(["git log --pretty=format:'%h' -n 1"], shell=True, stdout=PIPE).stdout.decode("UTF-8"))
    DEVELOPER_MODE = parse_as_boolean(getenv("DEVELOPER_MODE", False))
    # Настройки Telegram клиента
    API_ID = int(getenv("API_ID"))
    API_HASH = str(getenv("API_HASH"))
    BOT_TOKEN = str(getenv("BOT_TOKEN"))
    CHANNEL_ID = str(getenv("CHANNEL_ID"))
    # Настройки аккаунта Epic Games для использования их API
    EPIC_GAMES_EMAIL = str(getenv("EPIC_GAMES_EMAIL"))
    EPIC_GAMES_PASSWORD = str(getenv("EPIC_GAMES_PASSWORD"))
    LAUNCHER_TOKEN = str(getenv("LAUNCHER_TOKEN", "MzQ0NmNkNzI2OTRjNGE0NDg1ZDgxYjc3YWRiYjIxNDE6OTIwOWQ0YTVlMjVhNDU3ZmI5YjA3NDg5ZDMxM2I0MWE="))
    FORTNITE_TOKEN = str(getenv("FORTNITE_TOKEN", "ZWM2ODRiOGM2ODdmNDc5ZmFkZWEzY2IyYWQ4M2Y1YzY6ZTFmMzFjMjExZjI4NDEzMTg2MjYyZDM3YTEzZmM4NGQ="))
    # Настройки сообщества VK
    VK_TOKEN = str(getenv("VK_TOKEN"))
    VK_COMMUNITY_ID = int(getenv("VK_COMMUNITY_ID"))

    # Настройки Redis
    REDIS_HOST = str(getenv("REDIS_HOST", "127.0.0.1"))
    REDIS_PORT = int(getenv("REDIS_PORT", 6379))
except:
    logging.critical("Произошла ошибка при формировании настроек в конфигурационном файле.", exc_info=True)
    exit(1)
