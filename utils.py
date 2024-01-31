"""
Модуль утилит проекта:
MenuManager - формирования меню кнопок и их сообщений
collect_keyboard - получение клавиатуры
get_commands_dict - получения словаря комманд
"""

import csv
import logging
import os
import sys
from pathlib import Path
from typing import Optional

from vk_api.keyboard import VkKeyboard, VkKeyboardColor

from constants import (
    ENCODING,
    MENU_FILE_NAME,
    MENU_FOLDER,
    MAX_BUTONS,
    MENU_MESSAGE,
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
            self.__key_label = reader.fieldnames[0]
            self.__key_message = reader.fieldnames[1]
            self.__menu = data
        except IOError as error:
            logger.error(f"Ошибка чтения файла: {error}.")
            sys.exit()

    def get_menu_labels(self) -> list[str]:
        """Возвращает список лейблов для всех кнопок"""
        labels_list = []
        for row in self.__menu:
            labels_list.append(row[self.__key_label])
        return labels_list

    def get_message(self, label: str) -> Optional[str]:
        """
        Возвращает сообщение для заданной кнопки по лейблу.
        Если кнопки нет в меню, возвращает None.
        """
        for row in self.__menu:
            if row.get(self.__key_label, None) == label:
                return row.get(self.__key_message, None)
        return None

    def get_message_by_index(self, label: str) -> Optional[str]:
        """
        Возвращает сообщение для заданной кнопки по индексу.
        Если кнопки нет в меню, возвращает None.
        """
        for row in self.__menu:
            if label.isdigit() and self.__menu.index(row) == int(label):
                return row.get(self.__key_message, None)
        return None

    def get_preview_menu_labels(self) -> str:
        """Возвращает строку с описанием меню для кнопок"""
        preview = ""
        for label in self.get_menu_labels()[1::]:
            preview += f"{self.get_menu_labels().index(label)}. {label}\n"
        return preview

    def __write_file(self):
        """Метод перезаписи csv-файла"""
        os.makedirs(MENU_FOLDER, exist_ok=True)
        try:
            with open(filename, "w", newline="", encoding=ENCODING) as csvfile:
                fieldnames = [self.__key_label, self.__key_message]
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
            if row[self.__key_label] == label:
                row[self.__key_message] = new_message
        self.__write_file()

    def edit_label(self, label: str, new_label: str):
        """Изменение названия/лейбла для выбранной кнопки"""
        for row in self.__menu:
            if row[self.__key_label] == label:
                row[self.__key_label] = new_label
        self.__write_file()


def collect_keyboard(
    buttons: list, one_time=False, inline=False, color=VkKeyboardColor.POSITIVE
):
    """Функция создания клавиатуры."""
    keyboard = VkKeyboard(one_time=one_time, inline=inline)
    count_buttons = 0
    for button in buttons:
        keyboard.add_button(str(button), color=color)
        count_buttons += 1
        if count_buttons % MAX_BUTONS == 0:
            keyboard.add_line()
    return keyboard.get_keyboard()


def get_commands_dict():
    """Функция получения словаря комманд."""
    menu = MenuManager()
    keyboard_start = collect_keyboard(["Меню"])
    keyboard_menu = collect_keyboard(
        [i for i in range(1, len(menu.get_menu_labels()))]
    )
    keyboard_back = collect_keyboard(["Назад"])
    return dict(
        (
            ("Начать", (menu.get_message_by_index("0"), keyboard_start)),
            ("1", (menu.get_message_by_index("1"), keyboard_back)),
            ("2", (menu.get_message_by_index("2"), keyboard_back)),
            ("3", (menu.get_message_by_index("3"), keyboard_back)),
            ("4", (menu.get_message_by_index("4"), keyboard_back)),
            ("5", (menu.get_message_by_index("5"), keyboard_back)),
            ("6", (menu.get_message_by_index("6"), keyboard_back)),
            ("7", (menu.get_message_by_index("7"), keyboard_back)),
            (
                "Меню",
                (
                    MENU_MESSAGE.format(*menu.get_menu_labels()[1::]),
                    keyboard_menu,
                ),
            ),
            (
                "Назад",
                (
                    MENU_MESSAGE.format(*menu.get_menu_labels()[1::]),
                    keyboard_menu,
                ),
            ),
            (
                "6_for_adm",
                ((TO_ADMIN_DONAT, TO_USER_DONAT), keyboard_back),
            ),
            (
                "7_for_adm",
                ((TO_ADMIN_OTHER, TO_USER_OTHER), keyboard_back),
            ),
        )
    )
