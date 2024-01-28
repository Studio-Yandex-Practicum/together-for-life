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

menu = MenuManager()

cmd_answ = dict(
    (
        ("Начать", (menu.get_message_by_index("0"), keyboard_start)),
        ("Меню", (MENU_MESSAGE, keyboard_menu)),
    )
)
