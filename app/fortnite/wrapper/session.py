# -*- coding: utf-8 -*-
# Оригинал: https://github.com/nicolaskenner/python-fortnite-api-wrapper

from app import logging
from app import utils
from app.fortnite.wrapper import constants
from threading import Timer
from datetime import datetime, timedelta
import requests
import logging


class Session:
    def __init__(self, access_token, refresh_token, expires_at, fortnite_token):
        self.refresh_token = refresh_token
        self.expires_at = expires_at
        self.fortnite_token = fortnite_token
        self.session = requests.Session()
        self.session.headers.update({'Authorization': 'bearer {}'.format(access_token)})

        # Проверка, нужно ли обновлять токен (токен истекает через определенное время)
        def check_token():
            Timer(20.0, check_token).start()
            now = datetime.utcnow()
            if self.expires_at < (now - timedelta(seconds=60)):
                logging.info("Время действия токена доступа для Fortnite API истекло, генерируется новый.")

                self.refresh()

        check_token()

    def refresh(self):
        response = requests.post(constants.OAUTH_TOKEN,
                                 headers={'Authorization': 'basic {}'.format(self.fortnite_token)},
                                 data={'grant_type': 'refresh_token', 'refresh_token': '{}'.format(self.refresh_token),
                                       'includePerms': True}).json()
        access_token = response.get('access_token')
        self.session.headers.update({'Authorization': 'bearer {}'.format(access_token)})
        self.refresh_token = response.get('refresh_token')
        self.expires_at = utils.convert_iso_time(response.get('expires_at'))

        logging.info("Токен доступа для использования Fortnite API перегенерирован.")
        logging.debug("Access Token: {0}; Refresh Token: {1}; Expires At: {2}.".format(
            access_token, self.refresh_token, self.expires_at))

    def get(self, endpoint, params=None, headers=None):
        response = self.session.get(endpoint, params=params, headers=headers)
        return response.json()

    def post(self, endpoint, params=None, headers=None):
        response = self.session.post(endpoint, params=params, headers=headers)
        return response.json()

    @staticmethod
    def get_noauth(endpoint, params=None, headers=None):
        response = requests.get(endpoint, params=params, headers=headers)
        return response.json()

    @staticmethod
    def post_noauth(endpoint, params=None, headers=None):
        response = requests.post(endpoint, params=params, headers=headers)
        return response.json()
