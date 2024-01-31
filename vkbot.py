"""Модуль класса бота."""


import logging
import os

import vk_api
from vk_api.longpoll import VkEventType, VkLongPoll
from vk_api.keyboard import VkKeyboard, VkKeyboardColor, MAX_BUTTONS_ON_LINE

from constants import (
    CHECKING_UNIQUE,
    INLINE_KEYBOARD,
    EDIT_MODE_ITEM_TEMPLATE,
    NUMBERED_LABEL_TEMPLATE,
    SELECTED_MENU_ITEM_TEMPLATE,
    NEW_VALUE_QUESTION_TEMPLATE,
    EDIT_SUCCESS,
    EMPTY_VALUE,
    CANCEL_BUTTON_LABEL,
    ABORT_MASSAGE,
    BACKWARD_BUTTON_LABEL,
)

from utils import MenuManager

ZERO = 0
USER_ID = "user_id"
ONE = 1


logger = logging.getLogger(__name__)


class VKBot:
    """Класс ВК чат-бота."""

    def __init__(self, vk_token, vk_admin_user_id, menu: MenuManager):
        """Метод инициализации."""
        self.__vk_session = vk_api.VkApi(token=vk_token)
        self.__admin_id = int(vk_admin_user_id)
        self.__menu = menu
        # Параметры текущего режима редактирования меню
        # Режим редактирования меню включен (введено секретное слово)
        self.__menu_edit_mode = False
        # Выбранный индекс пункта меню для редактирования
        self.__current_edit_menu_index = None
        # Выбранный селектор (что редактировать: Заголовок или Информацию)
        self.__current_edit_selector = None
        # Словарь функций редактирования меню,
        # используется совместно с селектором
        # в обработчике __recive_new_value_handler
        self.__edit_functions = dict(
            (
                (self.__menu.key_label, self.__menu.edit_label),
                (self.__menu.key_message, self.__menu.edit_message),
            )
        )
        self.__menu_edit_key_word = os.getenv("MENU_EDIT_KEY_WORD")
        self.__make_service_command_book()

    def __make_service_command_book(self):
        """Составляет словарь команд режима редактирования меню для бота."""
        labels = self.__menu.get_menu_labels()
        self.__service_command_book = dict(
            (
                # Команда редактирования меню
                (
                    self.__menu_edit_key_word,
                    self.__recive_edit_menu_keyword_handler,
                ),
                # Команды для селектора (заголовок или информация)
                (self.__menu.key_label, self.__recive_edit_selector_handler),
                (self.__menu.key_message, self.__recive_edit_selector_handler),
            )
        )
        # Команды редактирования для пунктов меню в формате E0, ..., E7.
        for number in range(len(labels)):
            self.__service_command_book[
                EDIT_MODE_ITEM_TEMPLATE.format(number)
            ] = self.__recive_menu_item_to_edit_handler
        # Команда отмены
        self.__service_command_book[
            CANCEL_BUTTON_LABEL
        ] = self.__cancel_from_edit_mode_handler
        # Команда назад
        self.__service_command_book[
            BACKWARD_BUTTON_LABEL
        ] = self.__backward_in_edit_mode_handler

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
        # Точка входа для обработки сообщений редактирования меню
        self.__check_for_edit_menu_events(event.user_id, event.text)
        # Здесь обработка команд для чтения меню.
        pass

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

    def __add_cancel_button(self, keyboard: VkKeyboard):
        """Добавляет кнопку Отмена к объекту клавиатуры."""
        keyboard.add_button(CANCEL_BUTTON_LABEL, VkKeyboardColor.NEGATIVE)

    def __add_backward_button(self, keyboard: VkKeyboard):
        """Добавляет кнопку Назад к объекту клавиатуры."""
        keyboard.add_button(BACKWARD_BUTTON_LABEL, VkKeyboardColor.PRIMARY)

    def __get_selector_keyboard_json(self):
        """Возвращает JSON-объект клавиатуры для VK-api.
        Кнопки селектора (Заголовок, Информация)"""
        keyboard = self.__get_VK_keyboard()
        keyboard.add_button(self.__menu.key_label)
        keyboard.add_button(self.__menu.key_message)
        self.__add_cancel_button(keyboard)
        self.__add_backward_button(keyboard)
        return keyboard.get_keyboard()

    def __get_menu_items_to_edit_keyboard_json(self, menu_length: int):
        """Возвращает JSON-объект клавиатуры для VK-api.
        Кнопки выбора элемента меню для редактирования, вида:
        E0,...,E7, и Отмена."""
        keyboard = self.__get_VK_keyboard()
        for number in range(menu_length):
            keyboard.add_button(EDIT_MODE_ITEM_TEMPLATE.format(number))
            if (number + ONE) % MAX_BUTTONS_ON_LINE == ZERO:
                keyboard.add_line()
        self.__add_cancel_button(keyboard)
        return keyboard.get_keyboard()

    def __get_cancel_backward_keyboard_json(self):
        """Возвращает JSON-объект клавиатуры для VK-api.
        Кнопки Отмена и Назад."""
        keyboard = self.__get_VK_keyboard()
        self.__add_cancel_button(keyboard)
        self.__add_backward_button(keyboard)
        return keyboard.get_keyboard()

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

    def __check_for_edit_menu_events(self, user_id, text):
        """Метод проверяет, что сообщение от администратора группы.
        Запускает обработчик сообщений по словарю
        self.__service_command_book.
        Все сервисные обработчик сообщений получают в качестве
        аргументов user_id и text.
        """
        if user_id == self.__admin_id and text is not None:
            self.__service_command_book.get(
                text, self.__recive_new_value_handler
            )(user_id=user_id, text=text)

    def __recive_edit_menu_keyword_handler(self, **kwargs):
        """Обработчик сообщения команды редактирования меню.
        Выводит меню, включая стартовое сообщение, и нумерованные
        кнопки с префиксом для режима редактирования."""
        user_id = kwargs.get(USER_ID)
        labels = self.__menu.get_menu_labels()
        menu_message = ""
        for number in range(len(labels)):
            menu_message += NUMBERED_LABEL_TEMPLATE.format(
                number, labels[number]
            )
        self.__send_message(
            user_id=user_id,
            message_text=menu_message,
            keyboard=self.__get_menu_items_to_edit_keyboard_json(len(labels)),
        )
        self.__drop_edit_values()
        self.__menu_edit_mode = True

    def __recive_menu_item_to_edit_handler(self, user_id, text):
        """Обработчик для команды выбора пункта меню в режиме редактирования.
        Обрабатывает команд, вида E0,...,E7.
        Полученную команду сохраняет в self.__current_edit_menu_index.
        Выводит выбранный пункт меню включая заголовок с вопросом,
        что именно нужно редактировать, заголовок или информацию
        выводит соответсвующие кнопки.
        """
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
            # Кнопки селетора редактирования (заголовок или информация)
            self.__send_message(
                user_id=user_id,
                message_text=message,
                keyboard=self.__get_selector_keyboard_json(),
            )
        else:
            self.__drop_edit_values()

    def __recive_edit_selector_handler(self, user_id, text):
        """Обрабатывает сообщение с командой, что именно нужно
        редактировать, заголовок или информацию, в выбранном ранее
        пункте меню.
        Проверяет, что ранее был выбран пункт меню
        (self.__current_edit_menu_index).
        Сохраняет полученное значение в self.__current_edit_selector.
        Отправляет сообщение с запросом нового значения
        и кнопку Отмента.
        """
        if self.__menu_edit_mode and self.__current_edit_menu_index:
            self.__current_edit_selector = text
            message = NEW_VALUE_QUESTION_TEMPLATE.format(text)
            self.__send_message(
                user_id=user_id,
                message_text=message,
                keyboard=self.__get_cancel_backward_keyboard_json(),
            )
        else:
            self.__drop_edit_values()

    def __recive_new_value_handler(self, user_id, text):
        """Обработчик так называемого свободного текста,
        только в сервисном режиме (получено только от администратора).
        Проверяет, наличе сохраненных значений пункта меню и
        селектора (Заголовок или информация).
        """
        if (
            user_id == self.__admin_id
            and self.__menu_edit_mode
            and self.__current_edit_menu_index is not None
            and self.__current_edit_selector is not None
        ):
            if self.__is_text_valid(text):
                labels = self.__menu.get_menu_labels()
                menu_index = int(self.__current_edit_menu_index)
                self.__edit_functions.get(self.__current_edit_selector)(
                    labels[menu_index], text.strip()
                )
                self.__send_message(user_id, EDIT_SUCCESS)
            else:
                self.__send_message(user_id, EMPTY_VALUE)
        self.__drop_edit_values()

    def __cancel_from_edit_mode_handler(self, **kwargs):
        """Обработчик команды отмены редактирования.
        Cбрасывает сохраненные параметры режима редактирования меню.
        Выводит сообщение об отмене операции, если бот
        находился в режиме редактирования меню."""
        user_id = kwargs.get(USER_ID)
        if (
            self.__menu_edit_mode
            or self.__current_edit_menu_index is not None
            or self.__current_edit_selector is not None
        ):
            self.__send_message(user_id=user_id, message_text=ABORT_MASSAGE)
        self.__drop_edit_values()

    def __backward_in_edit_mode_handler(self, **kwargs):
        """Обработчик команды Назад в режиме редактирования.
        На стадии выбора селектора возвращает на стадию выбора пункта.
        На вводе нового значения возвращает на стадию выбора селектора.
        Сбрасывает соответсвующий параметр режима редактирования.
        Вызывает обработчик с восстановленными аргументами.
        В случае несоответсвия параметров режима редактирования,
        сбрасывает их.
        """
        user_id = kwargs.get(USER_ID)
        if (
            user_id == self.__admin_id
            and self.__menu_edit_mode
            and self.__current_edit_menu_index is not None
            and self.__current_edit_selector is not None
        ):
            self.__current_edit_selector = None
            self.__recive_menu_item_to_edit_handler(
                user_id=user_id,
                text=EDIT_MODE_ITEM_TEMPLATE.format(
                    self.__current_edit_menu_index
                ),
            )
        elif (
            user_id == self.__admin_id
            and self.__menu_edit_mode
            and self.__current_edit_menu_index is not None
        ):
            self.__current_edit_menu_index = None
            self.__recive_edit_menu_keyword_handler(
                user_id=user_id, text=self.__menu_edit_key_word
            )
        else:
            self.__drop_edit_values()

    def __is_text_valid(self, text: str) -> bool:
        """Проверяет, что текст сообщения не None,
        не пуст и не состоит только из пробелов."""
        return text is not None and text.strip() != ""
