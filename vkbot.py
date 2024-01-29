"""Модуль класса бота."""


import logging

import vk_api
from vk_api.longpoll import VkEventType, VkLongPoll
from vk_api.keyboard import VkKeyboard, MAX_BUTTONS_ON_LINE

from constants import (
    ECHO_MESSAGE_TEMPLATE,
    CHECKING_UNIQUE,
    MENU_EDIT_KEY_WORD,
    INLINE_KEYBOARD,
    EDIT_MODE_ITEM_TEMPLATE,
    NUMBERED_LABEL_TEMPLATE,
    SELECTED_MENU_ITEM_TEMPLATE,
    NEW_VALUE_QUESTION_TEMPLATE,
    EDIT_SUCCESS,
)

from utils import MenuManager

ZERO = 0
ONE = 1


logger = logging.getLogger(__name__)


class VKBot:
    """Класс ВК чат-бота."""

    def __init__(self, vk_token, vk_admin_user_id, menu: MenuManager):
        """Метод инициализации."""
        self.__vk_session = vk_api.VkApi(token=vk_token)
        self.__admin_id = int(vk_admin_user_id)
        self.__menu = menu

        self.__menu_edit_mode = False
        self.__current_edit_menu_index = None
        self.__current_edit_selector = None
        self.__make_service_command_book()

    def __make_service_command_book(self):
        labels = self.__menu.get_menu_labels()
        self.__service_command_book = dict(
            (
                # Команда редактирования меню
                (MENU_EDIT_KEY_WORD, self.___edit_menu_keyword_handler),
                # Команды для селектора (заголовок или информация)
                (self.__menu.key_label, self.__edit_selector_handler),
                (self.__menu.key_message, self.__edit_selector_handler),
            )
        )
        # Добавим команды редактирования для пунктов меню
        # в формате E0, ..., E7.
        for number in range(ZERO, len(labels)):
            self.__service_command_book[
                EDIT_MODE_ITEM_TEMPLATE.format(number)
            ] = self.__edit_menu_item_select_handler

    def vkbot_up(self):
        """Метод запуска бота."""
        logger.debug("Запуск Бота.")
        for event in VkLongPoll(self.__vk_session).listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                self.__message_handler(event)

    def __message_handler(self, event):
        """Метод разбора события новое сообщение."""
        logger.debug(
            f"От пользователя {event.user_id} получено сообщение: {event.text}"
        )
        message = ECHO_MESSAGE_TEMPLATE.format(event.text)
        self.__send_message(event.user_id, message)
        # Точка входа для обработки сообщений редактирования меню
        self.__check_for_service_event(event.user_id, event.text)

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

    def __get_VK_keyboard(self):
        """Создает и возвращает объект клавиатуры для бота VK."""
        return VkKeyboard(inline=INLINE_KEYBOARD)

    def __drop_edit_values(self):
        """Задает значения None для сохраненных
        для редактирования пункта меню и селектора
        (заголовок или информация),
        режим редактирования меню устанавливает в False.
        Вызывается, также в случаях когда, в обработчиках
        не получены ожидаемые значения.
        """
        self.__current_edit_menu_index = None
        self.__current_edit_selector = None
        self.__menu_edit_mode = False

    def __check_for_service_event(self, user_id, text):
        """Метод проверяет, что сообщение от администратора группы.
        Запускает обработчик сообщений по словарю
        self.__service_command_book.
        Все сервисные обработчик сообщений получают в качестве
        аргументов user_id и text.
        """
        if user_id == self.__admin_id and text is not None:
            self.__service_command_book.get(text, self.__free_text_handler)(
                user_id, text
            )

    def ___edit_menu_keyword_handler(self, user_id, text):
        """Обработчик сообщения команды редактирования меню.
        Выводит меню, включая стартовое сообщение, и нумерованные
        кнопки с префиксом для режима редактирования."""
        labels = self.__menu.get_menu_labels()
        menu_keyboard = self.__get_VK_keyboard()
        menu_message = ""
        button_labels = []
        for number in range(ZERO, len(labels)):
            button_labels.append(EDIT_MODE_ITEM_TEMPLATE.format(number))
            menu_keyboard.add_button(EDIT_MODE_ITEM_TEMPLATE.format(number))
            menu_message += NUMBERED_LABEL_TEMPLATE.format(
                number, labels[number]
            )
            if (number + ONE) % MAX_BUTTONS_ON_LINE == ZERO:
                menu_keyboard.add_line()
        self.__send_message(
            user_id=user_id,
            message_text=menu_message,
            keyboard=menu_keyboard.get_keyboard(),
        )
        self.__drop_edit_values()
        self.__menu_edit_mode = True

    def __edit_menu_item_select_handler(self, user_id, text):
        """Обработчик для команды выбора пункта меню в режиме редактирования.
        Обрабатывает команд, вида E0,...,E7.
        Полученную команду сохраняет в self.__current_edit_menu_index.
        Выводит выбранный пункт меню включя заголовок с вопросом,
        что именно нужно редактировать, заголовок или информацию
        выводт соответсвующие кнопки."""

        if self.__menu_edit_mode:
            self.__current_edit_menu_index = text[ONE:]
            labels = self.__menu.get_menu_labels()
            message = SELECTED_MENU_ITEM_TEMPLATE.format(
                self.__menu.key_label,
                labels[int(self.__current_edit_menu_index)],
                self.__menu.key_message,
                self.__menu.get_message_by_index(
                    self.__current_edit_menu_index
                ),
            )

            # Выводим пункт меню и информацию
            keyboard = self.__get_VK_keyboard()
            keyboard.add_button(self.__menu.key_label)
            keyboard.add_button(self.__menu.key_message)
            self.__send_message(
                user_id=user_id,
                message_text=message,
                keyboard=keyboard.get_keyboard(),
            )
        else:
            self.__drop_edit_values()

    def __edit_selector_handler(self, user_id, text):
        """Обрабатывает сообщение с командой, что именно нужно
        редактировать, заголовок или информацию, в выбранном ранее
        пункте меню.
        Проверяет, что ранее был выбран пункт меню
        (self.__current_edit_menu_index).
        Сохраняет полученное значение в self.__current_edit_selector.
        Отправляет сообщение с запросом нового значения.
        """
        if self.__menu_edit_mode and self.__current_edit_menu_index:
            self.__current_edit_selector = text
            message = NEW_VALUE_QUESTION_TEMPLATE.format(text)
            self.__send_message(user_id, message)
        else:
            self.__drop_edit_values()

    def __free_text_handler(self, user_id, text):
        """Обработчик так называемого свободного текста,
        только в сервисном режиме (получено тольк от администратора).
        Проверяет, наличе сохраненных значений пункта меню и
        селектора (Заголовок или информация).
        """
        # Блок обработки свободного текста,
        # только для режима редактирования меню
        if (
            user_id == self.__admin_id
            and self.__menu_edit_mode
            and self.__current_edit_menu_index is not None
            and self.__current_edit_selector is not None
        ):
            labels = self.__menu.get_menu_labels()
            menu_index = int(self.__current_edit_menu_index)
            if self.__current_edit_selector == self.__menu.key_label:
                self.__menu.edit_label(
                    label=labels[menu_index], new_label=text
                )
            if self.__current_edit_selector == self.__menu.key_message:
                self.__menu.edit_message(
                    label=labels[menu_index], new_message=text
                )
            message = EDIT_SUCCESS
            self.__send_message(user_id, message)
        self.__drop_edit_values()
