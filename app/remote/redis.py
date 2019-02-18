# -*- coding: utf-8 -*-

from app import logging
from app import config
import logging
import aioredis


class Redis:
    @staticmethod
    async def connection():
        try:
            response = await Redis.execute("ping")
            logging.debug("Returned response: " + str(response))

            if str(response['details']) == "PONG":
                logging.info("Соединение с Redis может быть установлено успешно.")
                return {"status": "OK", "details": response['details']}
            else:
                logging.error("Произошла ошибка при попытке установления соединения с Redis.")
                return {"status": "ERROR", "details": response['details']}
        except Exception as e:
            logging.error("Произошла ошибка при попытке установления соединения с Redis.", exc_info=True)
            return {"status": "ERROR", "details": str(e)}

    @classmethod
    async def execute(cls, *args, can_cause_exception=False):
        try:
            logging.debug("Passed arguments: " + str(args))

            redis_connection = await aioredis.create_connection(
                (config.REDIS_HOST, config.REDIS_PORT), encoding="UTF-8")
            result = await redis_connection.execute(*args, encoding="UTF-8")
            redis_connection.close()
            await redis_connection.wait_closed()

            return {"status": "OK", "details": result}
        except Exception as e:
            if not can_cause_exception:
                logging.error("Произошла ошибка при выполнении Redis запроса.", exc_info=True)
            else:
                logging.debug("Произошла ошибка при выполнении Redis запроса, но параметр can_cause_exception=True.",
                              exc_info=True)
            return {"status": "ERROR", "details": str(e)}
