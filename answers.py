from vk_api.keyboard import VkKeyboard, VkKeyboardColor

from constants import MENU_MESSAGE
from utils import MenuManager

keyboard_start = VkKeyboard(one_time=False, inline=False)
keyboard_start.add_button("Меню", color=VkKeyboardColor.POSITIVE)
keyboard_start = keyboard_start.get_keyboard()

keyboard_menu = VkKeyboard(one_time=False, inline=False)
keyboard_menu.add_button("1", color=VkKeyboardColor.POSITIVE)
keyboard_menu.add_button("2", color=VkKeyboardColor.POSITIVE)
keyboard_menu.add_button("3", color=VkKeyboardColor.POSITIVE)
keyboard_menu.add_button("4", color=VkKeyboardColor.POSITIVE)
keyboard_menu.add_line()
keyboard_menu.add_button("5", color=VkKeyboardColor.POSITIVE)
keyboard_menu.add_button("6", color=VkKeyboardColor.POSITIVE)
keyboard_menu.add_button("7", color=VkKeyboardColor.POSITIVE)
keyboard_menu = keyboard_menu.get_keyboard()

keyboard_back = VkKeyboard(one_time=False, inline=False)
keyboard_back.add_button("Назад", color=VkKeyboardColor.POSITIVE)
keyboard_back = keyboard_back.get_keyboard()

menu = MenuManager()

cmd_answ = dict(
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
            (MENU_MESSAGE.format(*menu.get_menu_labels()[1::]), keyboard_menu),
        ),
        (
            "Назад",
            (MENU_MESSAGE.format(*menu.get_menu_labels()[1::]), keyboard_menu),
        ),
    )
)
