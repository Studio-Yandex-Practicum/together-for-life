"""Модуль запуска бота."""

import logging
import os
import time

from dotenv import load_dotenv

from constants import RELOAD_TIME
from logger_config import init_globals_logging
from vkbot import VKBot

load_dotenv()

logger = logging.getLogger(__name__)


def main():
    """Функция работы бота."""
    while True:
        logger.debug("Запуск Бота.")
        try:
            bot_vk_chat = VKBot(os.getenv("VK_TOKEN"))
            bot_vk_chat.vkbot_up()
        except Exception as error:
            logger.error(f"Ошибка бота: {error}")
            time.sleep(RELOAD_TIME)


if __name__ == "__main__":
    init_globals_logging()
    main()
