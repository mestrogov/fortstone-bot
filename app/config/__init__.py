# -*- coding: utf-8 -*-

from subprocess import run, PIPE
from os import getenv
from sys import exit
from app.utils.parse_as_boolean import parse_as_boolean as parse_as_boolean
import logging


try:
    # Глобальные настройки приложения
    VERSION = str(getenv("VERSION", "Unknown"))
    COMMIT = str(run(["git log --pretty=format:'%h' -n 1"], shell=True, stdout=PIPE).stdout.decode("UTF-8"))
    DEVELOPER_MODE = parse_as_boolean(getenv("DEVELOPER_MODE", False))
    # Настройки Telegram клиента
    API_ID = int(getenv("API_ID"))
    API_HASH = str(getenv("API_HASH"))
    BOT_TOKEN = str(getenv("BOT_TOKEN"))

    # Настройки Redis
    REDIS_HOST = str(getenv("REDIS_HOST", "127.0.0.1"))
    REDIS_PORT = int(getenv("REDIS_PORT", 6379))
except (KeyError, TypeError):
    logging.critical("Произошла ошибка при попытке формирования конфигурационного файла.", exc_info=True)
    exit(1)
