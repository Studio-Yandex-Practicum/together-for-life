"""
Модуль утилит проекта:
MenuManager - формирования меню кнопок и их сообщений
collect_keyboard - получение клавиатуры
get_commands_dict - получения словаря команд
"""

import csv
import logging
import os
import sys
from pathlib import Path
from typing import Optional

from vk_api.keyboard import VkKeyboard, VkKeyboardColor

from constants import (
    BACKWARD_BUTTON_LABEL,
    ENCODING,
    MENU_BUTTON_LABEL,
    MENU_FILE_NAME,
    MENU_FOLDER,
    MAX_BUTTONS,
    PREVIEW_MENU_MESSAGE,
    START_BUTTON_LABEL,
    TO_ADMIN_DONAT,
    TO_USER_DONAT,
    TO_ADMIN_OTHER,
    TO_USER_OTHER,
)


BASE_DIR = Path(__file__).resolve().parent
filename = BASE_DIR / MENU_FOLDER / MENU_FILE_NAME

logger = logging.getLogger(__name__)


class MenuManager:
    """Класс формирования меню кнопок и их сообщений"""

    def __init__(self):
        """Чтение данных из csv-файла в список словарей"""
        data = []
        os.makedirs(MENU_FOLDER, exist_ok=True)
        try:
            with open(filename, "r", newline="", encoding=ENCODING) as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    data.append(row)
            self.key_label = reader.fieldnames[0]
            self.key_message = reader.fieldnames[1]
            self.__menu = data
        except IOError as error:
            logger.error(f"Ошибка чтения файла: {error}.")
            sys.exit()

    def get_menu_labels(self) -> list[str]:
        """Возвращает список лейблов для всех кнопок"""
        labels_list = []
        for row in self.__menu:
            labels_list.append(row[self.key_label])
        return labels_list

    def get_message(self, label: str) -> Optional[str]:
        """
        Возвращает сообщение для заданной кнопки по лейблу.
        Если кнопки нет в меню, возвращает None.
        """
        for row in self.__menu:
            if row.get(self.key_label, None) == label:
                return row.get(self.key_message, None)
        return None

    def get_label_by_index(self, index: str) -> Optional[str]:
        """
        Возвращает заголовок пункта меню по индексу.
        Если нет пункта с нужным индекс, возвращает None.
        """
        for row in self.__menu:
            if index.isdigit() and self.__menu.index(row) == int(index):
                return row.get(self.key_label, None)
        return None

    def get_message_by_index(self, label: str) -> Optional[str]:
        """
        Возвращает сообщение для заданной кнопки по индексу.
        Если кнопки нет в меню, возвращает None.
        """
        for row in self.__menu:
            if label.isdigit() and self.__menu.index(row) == int(label):
                return row.get(self.key_message, None)
        return None

    def get_preview_menu_labels(self, start_index: int = 1) -> str:
        """Возвращает строку с описанием меню для кнопок.
        Не обязательный аргумент start_index = 1."""
        preview = ""
        for label in self.get_menu_labels()[start_index::]:
            preview += f"{self.get_menu_labels().index(label)}. {label}\n"
        preview += PREVIEW_MENU_MESSAGE
        return preview

    def __write_file(self):
        """Метод перезаписи csv-файла"""
        os.makedirs(MENU_FOLDER, exist_ok=True)
        try:
            with open(filename, "w", newline="", encoding=ENCODING) as csvfile:
                fieldnames = [self.key_label, self.key_message]
                writer = csv.writer(csvfile)
                writer.writerow(fieldnames)
                new_menu_list = []
                for row in self.__menu:
                    new_menu_list.append(row.values())
                writer.writerows(new_menu_list)
        except IOError as error:
            logger.error(f"Ошибка чтения файла для записи: {error}.")

    def edit_message(self, label: str, new_message: str):
        """Изменение сообщения/информации для выбранной кнопки"""
        for row in self.__menu:
            if row[self.key_label] == label:
                row[self.key_message] = new_message
        self.__write_file()

    def edit_label(self, label: str, new_label: str):
        """Изменение названия/лейбла для выбранной кнопки"""
        for row in self.__menu:
            if row[self.key_label] == label:
                row[self.key_label] = new_label
        self.__write_file()

    def edit_button_info(self, button_index: str, label: str, message: str):
        """
        Запись нового состояния (Заголовок или информация)
        для выбранной кнопки по индексу
        """
        for row in self.__menu:
            if self.__menu.index(row) == int(button_index):
                row[self.key_label] = label
                row[self.key_message] = message
        self.__write_file()


def collect_keyboard(
    buttons, one_time=False, inline=False, color=VkKeyboardColor.POSITIVE
):
    """Функция создания клавиатуры."""
    keyboard = VkKeyboard(one_time=one_time, inline=inline)
    count_buttons = 0
    for button in buttons:
        keyboard.add_button(str(button), color=color)
        count_buttons += 1
        if count_buttons % MAX_BUTTONS == 0:
            keyboard.add_line()
    return keyboard.get_keyboard()


def get_commands_dict(menu: MenuManager):
    """Функция получения словаря команд."""
    keyboard_start = collect_keyboard([MENU_BUTTON_LABEL])
    keyboard_menu = collect_keyboard(
        [name for name in range(1, len(menu.get_menu_labels()))]
    )
    keyboard_back = collect_keyboard([BACKWARD_BUTTON_LABEL])
    return dict(
        (
            (
                START_BUTTON_LABEL,
                (menu.get_message_by_index("0"), keyboard_start),
            ),
            (
                MENU_BUTTON_LABEL,
                (menu.get_preview_menu_labels(), keyboard_menu),
            ),
            (
                BACKWARD_BUTTON_LABEL,
                (menu.get_preview_menu_labels(), keyboard_menu),
            ),
            ("6_for_adm", ((TO_ADMIN_DONAT, TO_USER_DONAT), keyboard_back)),
            ("7_for_adm", ((TO_ADMIN_OTHER, TO_USER_OTHER), keyboard_back)),
        )
    )
