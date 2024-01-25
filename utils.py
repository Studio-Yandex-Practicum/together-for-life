"""Модуль класса реализации чтения и записи файла csv."""
import csv
from pathlib import Path

from constants import ENCODING, MENU_FILE_NAME, PATH_TO_DATA


BASE_DIR = Path(__file__).resolve().parent
filename = BASE_DIR / PATH_TO_DATA / MENU_FILE_NAME


class MenuManager:
    """Класс формирования меню кнопок и их сообщений"""

    def __init__(self):
        """Чтение данных из csv-файла в список словарей"""
        data = []
        with open(filename, "r", newline="", encoding=ENCODING) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                data.append(row)
        self.__menu = data

    def get_menu_labels(self) -> list[str]:
        """Возвращает список лейблов для всех кнопок"""
        labels_list = []
        for row in self.__menu:
            labels_list.append(row["Заголовок(меню)"])
        return labels_list

    def get_message(self, label: str):
        """Возвращает сообщение для заданной кнопки по лейблу"""
        for row in self.__menu:
            if row["Заголовок(меню)"] == label:
                return row["Информация"]

    def __write_file(self):
        """Метод перезаписи csv-файла"""
        with open(filename, "w", newline="", encoding=ENCODING) as csvfile:
            fieldnames = ["Заголовок(меню)", "Информация"]
            writer = csv.writer(csvfile)
            writer.writerow(fieldnames)
            new_menu_list = []
            for row in self.__menu:
                new_menu_list.append(row.values())
            writer.writerows(new_menu_list)

    def edit_message(self, label: str, new_message: str):
        """Изменение сообщения/информации для выбранной кнопки"""
        for row in self.__menu:
            if row["Заголовок(меню)"] == label:
                row["Информация"] = new_message
        self.__write_file()

    def edit_label(self, label: str, new_label: str):
        """Изменение названия/лейбла для выбранной кнопки"""
        for row in self.__menu:
            if row["Заголовок(меню)"] == label:
                row["Заголовок(меню)"] = new_label
        self.__write_file()
