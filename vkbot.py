"""Модуль класса бота."""
import logging

import vk_api
from vk_api.longpoll import VkEventType, VkLongPoll

from answers import cmd_answ
from constants import CHECKING_UNIQUE

logger = logging.getLogger(__name__)


class VKBot:
    """Класс ВК чат-бота."""

    def __init__(self, vk_token):
        """Метод инициализации."""
        self.__vk_session = vk_api.VkApi(token=vk_token)

    def vkbot_up(self):
        """Метод запуска бота."""
        logger.debug("Запуск Бота.")
        for event in VkLongPoll(self.__vk_session).listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                self.__message_handler(event)

    def __message_handler(self, event):
        """Метод разбора события новое сообщение."""
        user_id, text = event.user_id, event.text
        logger.debug(f"От пользователя {user_id} получено сообщение: {text}")
        if cmd_answ.get(text) is not None:
            self.__send_message(user_id, *cmd_answ.get(text))
        elif self.__check_for_service_event(event):
            pass
        else:
            self.__send_message(user_id, *cmd_answ.get("Начать"))

    def __check_for_service_event(self, event):
        return False

    def __send_message(self, user_id, message_text, keyboard=None):
        """Метод отправки сообщений."""
        try:
            self.__vk_session.method(
                "messages.send",
                dict(
                    user_id=user_id,
                    message=message_text,
                    keyboard=keyboard,
                    random_id=CHECKING_UNIQUE,
                ),
            )
            logger.debug(
                f"Пользователю {user_id}, отправлено сообщение: {message_text}"
            )
        except Exception as error:
            logger.error(
                f"При отправке пользователю {user_id} сообщения: "
                f"{message_text}. Произошла ошибка: {error}."
            )
