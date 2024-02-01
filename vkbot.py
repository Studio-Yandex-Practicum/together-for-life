"""Модуль класса бота."""
import logging

import vk_api
from vk_api.longpoll import VkEventType, VkLongPoll

from constants import CHECKING_UNIQUE
from utils import collect_keyboard, get_commands_dict, MenuManager

logger = logging.getLogger(__name__)


class VKBot:
    """Класс ВК чат-бота."""

    def __init__(self, vk_token, vk_admin_user_id, menu: MenuManager):
        """Метод инициализации."""
        self.__vk_session = vk_api.VkApi(token=vk_token)
        self.__admin_id = int(vk_admin_user_id)
        self.__templ_date = dict()
        self.__menu = menu
        self.__cmd_answ = get_commands_dict(menu)

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

        if self.__cmd_answ.get(text) is not None:
            self.__send_message(user_id, *self.__cmd_answ.get(text))
        elif self.__menu.get_message_by_index(text) is not None:
            self.__send_message(
                user_id,
                self.__menu.get_message_by_index(text),
                collect_keyboard(["Назад"]),
            )
            self.__check_for_service_event(user_id, text)
        elif user_id in self.__templ_date:
            (massege_admin, massege_user), keyboard = self.__cmd_answ.get(
                self.__templ_date.get(user_id)
            )
            self.__send_message(
                self.__admin_id, massege_admin.format(user_id, text)
            )
            self.__send_message(user_id, massege_user, keyboard)
            self.__templ_date.pop(user_id)
        else:
            self.__send_message(user_id, *self.__cmd_answ("Начать"))

    def __check_for_service_event(self, user_id, text):
        """Метод проверки события, и записи в словарь."""
        if text in ["6", "7"]:
            self.__templ_date.setdefault(user_id, text + "_for_adm")

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
