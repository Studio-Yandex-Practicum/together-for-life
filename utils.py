import csv
from pathlib import Path

from constants import FILE_NAME, PATH_TO_DATA


BASE_DIR = Path(__file__).resolve().parent
filename = BASE_DIR / PATH_TO_DATA / FILE_NAME


class DataManager:
    """Класс формирования меню кнопок и их сообщений"""

    def __init__(self):
        """Чтение данных из csv-файла в словарь"""
        data = []
        with open(filename, "r") as file:
            reader = csv.DictReader(file)
            for i in reader:
                data.append(i)
        self._menu = data

    def get_menu_labels(self):
        """Возвращает список лейблов для всех кнопок"""
        labels_list = []
        for row in self._menu:
            labels_list.append(row["Заголовок(меню)"])
        return labels_list

    def get_message(self, label: str):
        """Возвращает сообщение для заданной кнопки по лейблу"""
        for row in self._menu:
            if row["Заголовок(меню)"] == label:
                return row["Информация"]

    def write_file(self):
        """Перезапись csv-файла"""
        with open(filename, "w", newline="", encoding="utf-8") as csvfile:
            csvfile.write("Заголовок(меню),Информация\n")
            for row in self._menu:
                label = row["Заголовок(меню)"]
                message = row["Информация"]
                csvfile.write(f"{label},{message}\n")

    def edit_message(self, label, new_message):
        """Изменение сообщения/информации для выбранной кнопки"""
        for row in self._menu:
            if row["Заголовок(меню)"] == label:
                row["Информация"] = f"{new_message}"
            self.write_file()

    def edit_label(self, label, new_label):
        """Изменение названия/лейбла для выбранной кнопки"""
        for row in self._menu:
            if row["Заголовок(меню)"] == label:
                row["Заголовок(меню)"] = new_label
            self.write_file()
