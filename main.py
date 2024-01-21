import logging


import os

from dotenv import load_dotenv

from constants import LOGGER_NAME
from logger_config import init_globals_logging
from vkbot import VKBot

load_dotenv()

logger = logging.getLogger(LOGGER_NAME)
logger.setLevel(logging.DEBUG)

if __name__ == "__main__":
    init_globals_logging()
    try:
        logger.debug(f"Запуск Бота - {LOGGER_NAME}")
        bot_vk_chat = VKBot(os.getenv("TOKEN"))
        bot_vk_chat.vkbot_up()
    except Exception as error:
        logger.error(f"Ошибка бота {LOGGER_NAME}: {error}")
