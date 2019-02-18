# -*- coding: utf-8 -*-

from app import config as config
from pyrogram import Client, MessageHandler, Filters
from app.telegram.commands.debug import debug as debug_command
from app.telegram.commands.start import start as start_command
from app.telegram.handlers.message import message as message_handler


def get_client():
    try:
        client = Client(session_name=config.BOT_TOKEN, api_id=config.API_ID, api_hash=config.API_HASH,
                        app_version="VKMessages v{0}".format(config.VERSION))
        client.add_handler(MessageHandler(start_command, Filters.command("start")))
        client.add_handler(MessageHandler(debug_command, Filters.command("debug")))
        # Этот MessageHandler должен быть обязательно последним
        client.add_handler(MessageHandler(message_handler))

        return client
    except Exception as e:
        return e
