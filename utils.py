import csv
from pathlib import Path

from constants import FILE_NAME, PATH_TO_DATA


BASE_DIR = Path(__file__).resolve().parent
filename = BASE_DIR / PATH_TO_DATA / FILE_NAME


class DataManager():
    """Класс формирования меню кнопок и их сообщений"""

    def __init__(self):
        """Чтение данных из csv-файла в словарь"""
        with open((filename), mode='r') as file:
            reader = csv.reader(file)
            header = next(reader)
            menu_dict = {}
            for row in reader:
                menu_dict[row[0]] = row[1]
        self._menu = menu_dict

    def edit_menu(self, new_menu_list):
        """Перезапись данных в csv-файле"""
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ["Заголовок(меню)", "Информация"]
            writer = csv.writer(csvfile)
            writer.writerow(fieldnames)
            writer.writerows(new_menu_list)

    def get_menu_labels(self):
        """Возвращает список лейблов для всех кнопок"""
        return list(self._menu)

    def get_message(self, button_name: str):
        """Возвращает сообщение для заданной кнопки по лейблу"""
        message = ""
        for name in self._menu:
            if button_name == name:
                message = self._menu[name]
                return message

    def edit_message(self, label, new_message):
        self._menu[label] = new_message
        new_menu_list = list(self._menu.items())
        self.edit_menu(new_menu_list)
