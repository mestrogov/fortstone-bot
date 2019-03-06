# -*- coding: utf-8 -*-

from app import config
from app.fortnite.wrapper.fortnite import Fortnite


def get_session():
    try:
        session = Fortnite(email=config.EPIC_GAMES_EMAIL, password=config.EPIC_GAMES_PASSWORD,
                           launcher_token=config.LAUNCHER_TOKEN, fortnite_token=config.FORTNITE_TOKEN)

        return session
    except Exception as e:
        return e
