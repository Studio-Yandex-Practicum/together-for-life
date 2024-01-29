"""Модуль класса реализации чтения и записи файла csv."""

import csv
import logging
import os
import sys
from pathlib import Path
from typing import Optional

from constants import ENCODING, MENU_FILE_NAME, MENU_FOLDER


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

    def edit_button_info(
            self, label_index: str,
            new_label: str,
            new_message: str):
        """
        Запись нового состояния (Заголовок или информация)
        для выбранной кнопки по индексу
        """
        for row in self.__menu:
            if self.__menu.index(row) == int(label_index):
                row[self.__key_label] = new_label
                row[self.__key_message] = new_message
        self.__write_file()
