# Глобальные настройки логгера
BACKUP_COUNT = 5
ENCODING = "UTF-8"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
FORMAT = "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
LOGGING_LEVEL = "DEBUG"
LOGS_FOLDER = "logs"
LOGS_FILE = "logfile.log"
MAX_BYTES = 50_000_000

# Константы утилиты чтения/записи csv-файла
MENU_FOLDER = "data"
MENU_FILE_NAME = "menu.csv"

# Константы ВК чат-бота
CHECKING_UNIQUE = 0
# 0 — проверка на уникальность не нужна.
# Любое другое число в пределах int32 — проверка на уникальность нужна.
MAX_BUTTONS = 4
TO_ADMIN_DONAT = "Получена обратная связь от пользователя {}: {}"
TO_ADMIN_OTHER = "Получен запрос от пользователя {}: {}"
TO_USER_DONAT = "Благодарим за участие."
TO_USER_OTHER = "Ваше обращение отправлено специалисту."

# Константы проекта
RELOAD_TIME = 15
# noqa - после падения, бот ждёт 15 сек до перезапуска

# Режим клавиатуры для VK inline
INLINE_KEYBOARD = True

# Шаблоны сообщений для обработчиков команд редактирования меню
# Дополнительный символ для кнопок меню в режиме редактирования
EDIT_MODE_ITEM_TEMPLATE = "E{}"
NUMBERED_LABEL_TEMPLATE = "{}. {} \n"
SELECTED_MENU_ITEM_TEMPLATE = "".join(
    (
        "{}:\n{}\n\n{}:\n{}\n\n",
        "Редактируем заголовок или информацию?",
    )
)

CANCEL_BUTTON_LABEL = "Отмена"
BACKWARD_BUTTON_LABEL = "Назад"
QUESTION_FOR_NEW_VALUE_TEMPLATE = "".join(
    (
        'Введите новое значение для "{}" пункта меню № {} ',
        'или нажмите кнопку "Отмена"',
    )
)
CONFIRM_NEW_VALUE_TEMPLATE = "".join(
    (
        "Для редактирования выбраны:\n{} пункта меню № {}.\n",
        'Сохранить изменение значения "{}" на "{}"?',
    )
)
EDIT_SUCCESS_MESSAGE = "Пункт меню успешно обновлен."
EMPTY_VALUE_MESSAGE = "Значение меню не может быть пустым."
ABORT_MESSAGE = "Операция отменена."
CONFIRM_BUTTON_LABEL = "Сохранить изменения"
START_BUTTON_LABEL = "Начать"
MENU_EDIT_ENV_KEY = "MENU_EDIT_KEY_WORD"
# Регулярное выражение для проверки нового значения для пункта меню
# Должно содержать как минимум одну букву.
NEW_VALUE_REGEXP = r"[a-zA-Zа-яА-Я]+"
