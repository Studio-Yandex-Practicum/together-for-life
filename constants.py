# Глобальные настройки логера
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

# Константы проекта
RELOAD_TIME = 15
# noga - после падения, бот ждёт 15 сек до перезапуска

# Ключевое слово для настройки меню
MENU_EDIT_KEY_WORD = "Edit menu"

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
NEW_VALUE_QUESTION_TEMPLATE = "".join(
    ("Введите новое значение для {} ", "или нажмите кнопку Отмена")
)
EDIT_SUCCESS = "Пункт меню успешно обновлен."
EMPTY_VALUE = "Значение меню не может быть пустым."
ABORT_MASSAGE = "Операция отменена."
