"""Модуль класса бота."""
import vk_api
from vk_api.longpoll import VkEventType, VkLongPoll

from constants import ECHO_MESSAGE, RANDOM_ID


class VKBot:
    """Класс ВК чат-бота."""

    def __init__(self, vk_token):
        """Метод инициализации."""
        self.__vk_token = vk_token

    def vkbot_up(
        self,
    ):
        """Метод запуска бота."""
        vk_session = vk_api.VkApi(token=self.__vk_token)
        for event in VkLongPoll(vk_session).listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                vk_session.method(
                    "messages.send",
                    dict(
                        user_id=event.user_id,
                        message=ECHO_MESSAGE.format(event.text),
                        keyboard=None,
                        random_id=RANDOM_ID,
                    ),
                )
