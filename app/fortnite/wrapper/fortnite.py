# -*- coding: utf-8 -*-
# Оригинал: https://github.com/nicolaskenner/python-fortnite-api-wrapper

from app import logging
from app import utils
from app.fortnite.wrapper.session import Session
from app.fortnite.wrapper import constants
import requests
import logging


class Fortnite:
    def __init__(self, fortnite_token, launcher_token, password, email):
        password_response = requests.post(constants.OAUTH_TOKEN,
                                          headers={'Authorization': 'basic {}'.format(launcher_token)},
                                          data={'grant_type': 'password', 'username': '{}'.format(email),
                                                'password': '{}'.format(password), 'includePerms': True}).json()
        access_token = password_response.get('access_token')

        exchange_response = requests.get(constants.OAUTH_EXCHANGE,
                                         headers={'Authorization': 'bearer {}'.format(access_token)}).json()
        code = exchange_response.get('code')

        token_response = requests.post(constants.OAUTH_TOKEN, headers={'Authorization': 'basic {}'.format(fortnite_token)},
                                       data={'grant_type': 'exchange_code', 'exchange_code': '{}'.format(code),
                                             'includePerms': True, 'token_type': 'egl'}).json()

        access_token = token_response.get('access_token')
        refresh_token = token_response.get('refresh_token')
        expires_at = utils.convert_iso_time(token_response.get('expires_at'))
        self.session = Session(access_token, refresh_token, expires_at, fortnite_token)

        logging.info("Токен доступа для использования Fortnite API получен.")
        logging.debug("Access Token: {0}; Refresh Token: {1}; Expires At: {2}.".format(
            access_token, refresh_token, expires_at))

    def account_lookup(self, username):
        """Return object containing player name and id"""
        response = self.session.get(constants.ACCOUNT_LOOKUP.format(username))
        return response

    def player_stats(self, username):
        """Return object containing Battle Royale stats"""
        player_id = self.account_lookup(username)['id']
        response = self.session.get(constants.PLAYER_STATS.format(player_id))
        return response

    def item_store(self):
        """Return current store items. This method only works for the authenticated account."""
        response = self.session.get(constants.ITEM_STORE)
        return response

    @staticmethod
    def ingame_news():
        """Get the current news on fortnite from battle royale and save the world."""
        response = Session.get_noauth(endpoint=constants.INGAME_NEWS, headers={'Accept-Language': 'ru'})
        ingame_news = {
            "battleroyale": {
                "last_modified": response['battleroyalenews']['lastModified'],
                "locale": response['battleroyalenews']['_locale'],
                "news": response['battleroyalenews']['news']['messages']
            },
            "savetheworld": {
                "last_modified": response['savetheworldnews']['lastModified'],
                "locale": response['savetheworldnews']['_locale'],
                "news": response['savetheworldnews']['news']['messages']
            }
        }
        return ingame_news

    @staticmethod
    def server_status():
        """Check the status of the Fortnite servers. Returns True if up and False if down."""
        response = Session.get_noauth(endpoint=constants.SERVER_STATUS)
        if response[0]['status'] == 'UP':
            return True
        else:
            return False

    @staticmethod
    def fortnite_patch_notes(posts_per_page=5, offset=0, locale='ru-RU', category='patch notes'):
        """Get a list of recent patch notes for fortnite. Can return other blogs from epicgames.com"""
        params = {'category': category, 'postsPerPage': posts_per_page, 'offset': offset, 'locale': locale}
        response = Session.get_noauth(endpoint=constants.FORTNITE_PATCH_NOTES, params=params)
        return response
