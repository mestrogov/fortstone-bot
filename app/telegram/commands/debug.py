# -*- coding: utf-8 -*-

from app import logging
from app import config as config
import logging


def debug(client, message):
    try:
        client.send_message(
            message.from_user.id,
            "Ниже находится информация, которая может оказаться полезной."
            "\n\n**Информация о приложении:** \n`Version: {0}`\n`Commit: {1}`\n`Developer Mode: {2}`"
            "\n\n**Информация о пользователе:** \n`User ID: {3}`\n`Message ID: {4}`\n`Language Code: {5}`".format(
                config.VERSION, config.COMMIT, config.DEVELOPER_MODE, message.from_user.id, message.message_id,
                message.from_user.language_code))
    except Exception as e:
        logging.error("Произошла ошибка при выполнении команды /debug.", exc_info=True)
        return e
