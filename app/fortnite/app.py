# -*- coding: utf-8 -*-

from app import config
from pfaw import Fortnite


def get_client():
    try:
        client = Fortnite(email=config.EPIC_GAMES_EMAIL, password=config.EPIC_GAMES_PASSWORD,
                          launcher_token=config.LAUNCHER_TOKEN, fortnite_token=config.FORTNITE_TOKEN)

        return client
    except Exception as e:
        return e
