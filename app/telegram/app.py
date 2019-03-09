# -*- coding: utf-8 -*-

from app import config
from pyrogram import Client, MessageHandler, Filters
from app.telegram.commands.debug import debug as debug_command
from app.telegram.commands.start import start as start_command
from app.telegram.commands.status import status as status_command
from app.telegram.commands.store import store as store_command
from app.telegram.commands.news import news as news_command
from app.telegram.handlers.message import message as message_handler


def get_client():
    try:
        client = Client(session_name=config.BOT_TOKEN, api_id=config.API_ID, api_hash=config.API_HASH,
                        app_version="FortniteArchives v{0}".format(config.VERSION))

        client.add_handler(MessageHandler(start_command,
                                          Filters.command(["start", "start@fnarchivesbot"])))
        client.add_handler(MessageHandler(debug_command,
                                          Filters.command(["debug", "debug@fnarchivesbot"])))
        client.add_handler(MessageHandler(status_command,
                                          Filters.command(["status", "status@fnarchivesbot"])))
        client.add_handler(MessageHandler(store_command,
                                          Filters.command(["store", "store@fnarchivesbot"])))
        client.add_handler(MessageHandler(news_command,
                                          Filters.command(["news", "news@fnarchivesbot"])))
        # Этот MessageHandler должен быть обязательно последним
        client.add_handler(MessageHandler(message_handler))

        return client
    except Exception as e:
        return e
