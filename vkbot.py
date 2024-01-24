"""Модуль класса бота."""
import logging

import vk_api
from vk_api.longpoll import VkEventType, VkLongPoll

from constants import ECHO_MESSAGE_TEMPLATE, CHECKING_UNIQUE

logger = logging.getLogger(__name__)


class VKBot:
    """Класс ВК чат-бота."""

    def __init__(self, vk_token):
        """Метод инициализации."""
        self.__vk_session = vk_api.VkApi(token=vk_token)

    def vkbot_up(
        self,
    ):
        """Метод запуска бота."""
        for event in VkLongPoll(self.__vk_session).listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                logger.debug(f"Получено сообщение: {event.text}")
                self.__vk_session.method(
                    "messages.send",
                    dict(
                        user_id=event.user_id,
                        message=ECHO_MESSAGE_TEMPLATE.format(event.text),
                        keyboard=None,
                        random_id=CHECKING_UNIQUE,
                    ),
                )
                logger.debug(
                    "Отправлено сообщение: "
                    f"{ECHO_MESSAGE_TEMPLATE.format(event.text)}"
                )
