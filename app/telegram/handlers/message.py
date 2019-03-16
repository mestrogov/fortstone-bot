# -*- coding: utf-8 -*-

from app import logging
from app import config
from app.vk.session import Session as vk_session
from tempfile import NamedTemporaryFile
import logging


def message(client, message):
    logging.critical(message)
    if message['chat']['id'] == config.CHANNEL_ID and config.VK_TOKEN and config.VK_COMMUNITY_ID:
        vk_client = vk_session(config.VK_TOKEN, version=5.92)
        logging.debug(f"Клиент VK: {vk_client}.")

        try:
            assert message['photo']

            with NamedTemporaryFile(suffix=".png") as photo_file:
                client.download_media(message['photo'], photo_file.name)

                upload_server = vk_client.get("photos.getWallUploadServer")['response']['upload_url']
                logging.debug(f"Сервер для загрузки фотографии: {upload_server}")
                uploaded_photo = vk_client.post(upload_server, files={"upload_file": open(photo_file.name, "rb")})
                logging.debug(f"Получен ответ после загрузки фотографии: {uploaded_photo}.")
        except AssertionError:
            pass

        params = {"owner_id": config.VK_COMMUNITY_ID, "from_group": 1, "message": message['text']}
        post = vk_client.post("wall.post", params=params)

        logging.debug(f"Опубликовано сообщение из канала в сообщество VK, ответ: {post}.")
        return post
