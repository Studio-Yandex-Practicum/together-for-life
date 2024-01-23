import csv

from constants import PATH_TO_DATA


def get_menu_dict():
    with open((PATH_TO_DATA), mode='r') as file:
        reader = csv.reader(file)
        header = next(reader)
        menu_dict = {}
        for row in reader:
            menu_dict[row[0]] = row[1]
        return menu_dict


def get_menu_labels():
    return list(get_menu_dict())


def get_message(button_name: str):
    message = ""
    for name in get_menu_dict():
        if button_name == name:
            message = get_menu_dict()[name]
            return message
