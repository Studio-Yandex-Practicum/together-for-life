"""Модуль класса бота."""


import logging
import os
import re
from typing import Dict

import vk_api
from vk_api.keyboard import MAX_BUTTONS_ON_LINE, VkKeyboard, VkKeyboardColor
from vk_api.longpoll import VkEventType, VkLongPoll

from constants import (
    ABORT_MESSAGE,
    BACKWARD_BUTTON_LABEL,
    CANCEL_BUTTON_LABEL,
    CHECKING_UNIQUE,
    CONFIRM_BUTTON_LABEL,
    CONFIRM_NEW_VALUE_TEMPLATE,
    EDIT_MODE_ITEM_TEMPLATE,
    EDIT_SUCCESS_MESSAGE,
    EMPTY_VALUE_MESSAGE,
    INLINE_KEYBOARD,
    MENU_EDIT_ENV_KEY,
    NEW_VALUE_QUESTION_TEMPLATE,
    NEW_VALUE_REGEXP,
    SELECTED_MENU_ITEM_TEMPLATE,
    START_BUTTON_LABEL,
)
from utils import collect_keyboard, get_commands_dict, MenuManager

ONE = 1
USER_ID = "user_id"
ZERO = 0


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
        # Введенное новое значение для пункта меню.
        self.__current_new_value = None
        # Словарь функций редактирования меню,
        # используется совместно с селектором
        # в обработчике __receive_new_value_handler
        self.__edit_functions = dict(
            (
                (self.__menu.key_label, self.__menu.edit_label),
                (self.__menu.key_message, self.__menu.edit_message),
            )
        )
        # Словарь функций чтения элементов меню,
        # используется совместно с селектором
        # в обработчике __receive_new_value_handler
        self.__get_menu_item_functions = dict(
            (
                (self.__menu.key_label, self.__menu.get_label_by_index),
                (self.__menu.key_message, self.__menu.get_message_by_index),
            )
        )
        self.__menu_edit_key_word = os.getenv(MENU_EDIT_ENV_KEY)
        self.__make_service_command_book()
        # Сигнальный аттрибут, обработана текущая команда или нет.
        self.__is_current_command_handled = False
        # Словарь состояний для пунктов чтения меню,
        # где предусмотрена отправка сообщений администратору
        self.__temp_data: Dict[int, str] = {}
        # словарь команд чтения меню
        self.__cmd_answ = get_commands_dict(self.__menu)

    def __make_service_command_book(self):
        """Составляет словарь команд режима редактирования меню для бота.
        Ключ - команда (строка)
        Значение - метод настоящего класса, который обрабатывает команду."""
        labels = self.__menu.get_menu_labels()
        self.__service_command_book = dict(
            (
                # Команда редактирования меню
                (
                    self.__menu_edit_key_word,
                    self.__receive_edit_menu_keyword_handler,
                ),
                # Команды для селектора (заголовок или информация)
                (self.__menu.key_label, self.__receive_edit_selector_handler),
                (
                    self.__menu.key_message,
                    self.__receive_edit_selector_handler,
                ),
                # Команда отмены режима редактирования
                (CANCEL_BUTTON_LABEL, self.__cancel_from_edit_mode_handler),
                # Команда назад режима редактирования
                (BACKWARD_BUTTON_LABEL, self.__backward_in_edit_mode_handler),
                # Команда сохранить изменения
                (
                    CONFIRM_BUTTON_LABEL,
                    self.__receive_confirm_in_edit_mode_handler,
                ),
            )
        )
        # Команды редактирования для пунктов меню в формате E0, ..., E7.
        for number in range(len(labels)):
            self.__service_command_book[
                EDIT_MODE_ITEM_TEMPLATE.format(number)
            ] = self.__receive_menu_item_to_edit_handler

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
        # Точка входа для обработки сообщений редактирования меню
        self.__check_for_edit_menu_events(user_id, text)
        # Если команда не обработана в блоке режима редактирования,
        # то продолжить обработку в блоке чтения меню.
        if not self.__is_current_command_handled:
            # Здесь обработка команд для чтения меню.
            if self.__cmd_answ.get(text) is not None:
                self.__send_message(user_id, *self.__cmd_answ.get(text))
            elif self.__menu.get_message_by_index(text) is not None:
                self.__send_message(
                    user_id,
                    self.__menu.get_message_by_index(text),
                    collect_keyboard(["Назад"]),
                )
                self.__check_for_service_event(user_id, text)
            elif user_id in self.__temp_data:
                (message_admin, message_user), keyboard = self.__cmd_answ.get(
                    self.__temp_data.get(user_id)
                )
                self.__send_message(
                    self.__admin_id, message_admin.format(user_id, text)
                )
                self.__send_message(user_id, message_user, keyboard)
                self.__temp_data.pop(user_id)
            else:
                self.__send_message(user_id, *self.__cmd_answ["Начать"])
        self.__is_current_command_handled = False

    def __check_for_service_event(self, user_id, text):
        """Метод проверки события, и записи в словарь."""
        if text in ["6", "7"]:
            self.__temp_data.setdefault(user_id, text + "_for_adm")

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

    def __get_confirm_stage_keyboard_json(self):
        """Возвращает JSON-объект клавиатуры для VK-api.
        Кнопки Сохранить изменения, Назад и Отмена.
        Используется на четвертой стадии режима редактирования
        для запроса подтверждения сохранения нового значения."""
        keyboard = self.__get_VK_keyboard()
        keyboard.add_button(CONFIRM_BUTTON_LABEL, VkKeyboardColor.POSITIVE)
        self.__add_cancel_button(keyboard)
        self.__add_backward_button(keyboard)
        return keyboard.get_keyboard()

    def __get_start_keyboard_json(self):
        keyboard = self.__get_VK_keyboard()
        keyboard.add_button(START_BUTTON_LABEL)
        return keyboard.get_keyboard()

    def __drop_edit_values(self):
        """Задает значения None для сохраненных
        для редактирования пункта меню и селектора
        (заголовок или информация),
        режим редактирования меню устанавливает в False.
        Вызывается, также в случаях когда, в обработчиках
        не получены ожидаемые значения или поступили смешанные
        команды, не соответствующие текущим значения параметров
        режима редактирования.
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
        По команде в text из словаря извлекается метод-обработчик,
        в него передаются user_id и поступивший text.
        Если подходящей команды в словаре нет, вызывается метод
        self.__receive_new_value_handler, он обрабатывает свободный текст.
        """
        if user_id == self.__admin_id and text is not None:
            self.__service_command_book.get(
                text, self.__receive_new_value_handler
            )(user_id=user_id, text=text)

    def __receive_edit_menu_keyword_handler(self, **kwargs):
        """Первая стадия редактирования - получено секретное слово.
        Обработчик сообщения команды редактирования меню.
        Выводит меню, включая стартовое сообщение, и нумерованные
        кнопки с префиксом для режима редактирования."""
        user_id = kwargs.get(USER_ID)
        labels = self.__menu.get_menu_labels()
        self.__send_message(
            user_id=user_id,
            message_text=self.__menu.get_preview_menu_labels(start_index=ZERO),
            keyboard=self.__get_menu_items_to_edit_keyboard_json(len(labels)),
        )
        # Сброс параметров режима редактирования
        self.__drop_edit_values()
        # Устанавливаем, что бот получил секретное слово
        # и вошел в режим редактирования меню.
        self.__menu_edit_mode = True
        self.__is_current_command_handled = True

    def __receive_menu_item_to_edit_handler(self, user_id, text):
        """Вторая стадия режима редактирования - выбран пункт меню.
        Обработчик для команды выбора пункта меню в режиме редактирования.
        Обрабатывает команды, вида E0,...,E7.
        Полученную команду сохраняет в self.__current_edit_menu_index.
        Выводит выбранный пункт меню включая заголовок с вопросом,
        что именно нужно редактировать, заголовок или информацию
        выводит соответствующие кнопки.
        """
        # Проверяется, что ранее было получено секретное слово.
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
            # Кнопки селектора редактирования (заголовок или информация)
            self.__send_message(
                user_id=user_id,
                message_text=message,
                keyboard=self.__get_selector_keyboard_json(),
            )
            self.__is_current_command_handled = True
        else:
            # Если ранее секретного слова не было, но поступила команда
            # с пунктом меню в формате редактирования - сброс параметров
            # редактирования.
            self.__drop_edit_values()

    def __receive_edit_selector_handler(self, user_id, text):
        """Третья стадия - выбрано, что редактировать
        (Заголовок или Информация).
        Обрабатывает сообщение с командой, что именно нужно
        редактировать, заголовок или информацию, в выбранном ранее
        пункте меню.
        Проверяет, что ранее был выбран пункт меню
        (self.__current_edit_menu_index) и получено секретное слово.
        Сохраняет полученное значение в self.__current_edit_selector.
        Отправляет сообщение с запросом нового значения
        и кнопку Отмена.
        """
        if self.__menu_edit_mode and self.__current_edit_menu_index:
            self.__current_edit_selector = text
            message = NEW_VALUE_QUESTION_TEMPLATE.format(
                text, self.__current_edit_menu_index
            )
            self.__send_message(
                user_id=user_id,
                message_text=message,
                keyboard=self.__get_cancel_backward_keyboard_json(),
            )
            self.__is_current_command_handled = True
        else:
            # При поступлении смешанных команд - сброс
            # параметров редактирования.
            self.__drop_edit_values()

    def __receive_new_value_handler(self, user_id, text):
        """Четвертая стадия - получено новое значение для пункта меню.
        Обработчик так называемого свободного текста
        (получено только от администратора).
        Проверяет, наличе сохраненных значений пункта меню и
        селектора (Заголовок или информация), ввод секретного слова,
        и что команда поступила от администратора.
        Выводит запрос на подтверждение изменений.
        """
        if (
            user_id == self.__admin_id
            and self.__menu_edit_mode
            and self.__current_edit_menu_index is not None
            and self.__current_edit_selector is not None
        ):
            if self.__is_text_valid(text):
                # Запоминаем новое значение
                self.__current_new_value = text.strip()
                # Из словаря по ключу - селектору, извлекается метод
                # чтения (для заголовка или информации)
                old_value = self.__get_menu_item_functions.get(
                    self.__current_edit_selector
                )(self.__current_edit_menu_index)
                message = CONFIRM_NEW_VALUE_TEMPLATE.format(
                    self.__current_edit_selector,
                    self.__current_edit_menu_index,
                    old_value,
                    self.__current_new_value,
                )
                self.__send_message(
                    user_id=user_id,
                    message_text=message,
                    keyboard=self.__get_confirm_stage_keyboard_json(),
                )
            else:
                # Если введенное значение не корректно (пустое)
                self.__send_message(
                    user_id=user_id,
                    message_text=EMPTY_VALUE_MESSAGE,
                    keyboard=self.__get_cancel_backward_keyboard_json(),
                )
            self.__is_current_command_handled = True
        else:
            # Если ввод текста не соответствует текущей стадии режима
            # редактирования, или поступили смешанные команды, то
            # сброс параметров редактирования. Команда не обработана.
            self.__drop_edit_values()
            self.__is_current_command_handled = False

    def __cancel_from_edit_mode_handler(self, **kwargs):
        """Обработчик команды отмены редактирования.
        Сбрасывает сохраненные параметры режима редактирования меню.
        Выводит сообщение об отмене операции, если бот
        находился в режиме редактирования меню."""
        user_id = kwargs.get(USER_ID)
        if (
            self.__menu_edit_mode
            or self.__current_edit_menu_index is not None
            or self.__current_edit_selector is not None
        ):
            self.__send_message(user_id=user_id, message_text=ABORT_MESSAGE)
            self.__is_current_command_handled = True
        self.__drop_edit_values()

    def __backward_in_edit_mode_handler(self, **kwargs):
        """Обработчик команды Назад в режиме редактирования.
        На стадии выбора селектора возвращает на стадию выбора пункта.
        На вводе нового значения возвращает на стадию выбора селектора.
        Сбрасывает соответствующий параметр режима редактирования.
        Вызывает обработчик с восстановленными аргументами.
        В случае несоответствия параметров режима редактирования,
        сбрасывает их.
        """
        user_id = kwargs.get(USER_ID)
        # Если бот на четвертой стадии редактирования -
        # введено новое значение.
        if (
            user_id == self.__admin_id
            and self.__menu_edit_mode
            and self.__current_edit_menu_index is not None
            and self.__current_edit_selector is not None
            and self.__current_new_value is not None
        ):
            self.__current_new_value = None
            self.__receive_edit_selector_handler(
                user_id=user_id, text=self.__current_edit_selector
            )
        # Если бот на третьей стадии - выбран селектор,
        # ожидается ввод нового значения.
        elif (
            user_id == self.__admin_id
            and self.__menu_edit_mode
            and self.__current_edit_menu_index is not None
            and self.__current_edit_selector is not None
        ):
            self.__current_edit_selector = None
            self.__receive_menu_item_to_edit_handler(
                user_id=user_id,
                text=EDIT_MODE_ITEM_TEMPLATE.format(
                    self.__current_edit_menu_index
                ),
            )
            self.__is_current_command_handled = True
        # Если бот на второй стадии - выбран пункт меню для редактирования,
        # ожидается ввод селектора.
        elif (
            user_id == self.__admin_id
            and self.__menu_edit_mode
            and self.__current_edit_menu_index is not None
        ):
            self.__current_edit_menu_index = None
            self.__receive_edit_menu_keyword_handler(
                user_id=user_id, text=self.__menu_edit_key_word
            )
            self.__is_current_command_handled = True
        # Если бот на первой стадии - введено секретное слово,
        # ожидается выбор пункта меню, и в остальных случаях.
        else:
            self.__drop_edit_values()
            # self.__is_current_command_handled = True

    def __is_text_valid(self, text: str) -> bool:
        """Проверяет, что текст сообщения не None,
        не пуст, не состоит только из пробелов и
        содержит хотя бы одну букву."""
        return (
            text is not None
            and text.strip() != ""
            and re.search(NEW_VALUE_REGEXP, text)
        )

    def __receive_confirm_in_edit_mode_handler(self, **kwargs):
        """Пятая стадия редактирования - получение команды подтверждения
        изменений пункта меню. Проверяет текущую стадию редактирования,
        изменяет пункт меню."""
        user_id = kwargs.get(USER_ID)
        if (
            user_id == self.__admin_id
            and self.__menu_edit_mode
            and self.__current_edit_menu_index is not None
            and self.__current_edit_selector is not None
            and self.__current_new_value is not None
        ):
            labels = self.__menu.get_menu_labels()
            menu_index = int(self.__current_edit_menu_index)
            # Из словаря по ключу - селектору, извлекается метод
            # редактирования (для заголовка или информации)
            self.__edit_functions.get(self.__current_edit_selector)(
                labels[menu_index], self.__current_new_value.strip()
            )
            self.__send_message(
                user_id=user_id,
                message_text=EDIT_SUCCESS_MESSAGE,
                keyboard=self.__get_start_keyboard_json(),
            )
            # Обновляем словарь команд для режима чтения
            self.__cmd_answ = get_commands_dict(self.__menu)
            self.__is_current_command_handled = True
        else:
            # Если поступили смешанные команды, то
            # команда не обработана
            self.__is_current_command_handled = False
        self.__drop_edit_values()
