# -*- coding: utf-8 -*-

from app import logging
import logging


def start(client, message):
    try:
        client.send_message(message.chat.id,
                            "Приветствую тебя, {0} {1}!"
                            "\n\nЯ пока что являюсь секретным Ботом и про себя не могу ничего рассказывать.".format(
                                message.from_user.first_name, message.from_user.last_name))
    except Exception as e:
        logging.error("Произошла ошибка при выполнении команды /start.", exc_info=True)
        return e
