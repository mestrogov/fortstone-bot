# -*- coding: utf-8 -*-

from app import logging
import logging


def start(client, message):
    try:
        client.send_message(
            message.from_user.id,
            "Приветствую тебя, {0} {1}!"
            "\n\nБлагодарю за возникший интерес ко мне. Я являюсь Ботом, который помогает делать работу в канале "
            "Фортнайтер. К сожалению, тебе ничего предложить не могу :(")
    except Exception as e:
        logging.error("Произошла ошибка при выполнении команды /start.", exc_info=True)
        return e
