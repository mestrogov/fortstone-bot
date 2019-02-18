# -*- coding: utf-8 -*-
# Взято отсюда: https://github.com/eternnoir/pyTelegramBotAPI/blob/master/telebot/util.py

from app.telegram.utils.is_command import is_command


def extract_command(text):
    """
    Extracts the command from `text` (minus the '/') if `text` is a command (see is_command).
    If `text` is not a command, this function returns None.
    Examples:
    extract_command('/help'): 'help'
    extract_command('/help@BotName'): 'help'
    extract_command('/search black eyed peas'): 'search'
    extract_command('Good day to you'): None
    :param text: String to extract the command from
    :return: the command if `text` is a command (according to is_command), else None.
    """

    return text.split()[0].split('@')[0][1:] if is_command(text) else None
