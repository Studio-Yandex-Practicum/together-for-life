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
ECHO_MESSAGE_TEMPLATE = "Поступило сообщение: {}."
CHECKING_UNIQUE = 0
# 0 — проверка на уникальность не нужна.
# Любое другое число в пределах int32 — проверка на уникальность нужна.
MENU_MESSAGE = "1. {}\n2. {}\n3. {}\n4. {}\n5. {}\n6. {}\n7. {}"
TO_ADMIN_DONAT = "Получена обратная связь от пользователя {}: {}"
TO_USER_DONAT = "Благодарим за участие."
TO_ADMIN_OTHER = "Получен запрос от пользователя {}: {}"
TO_USER_OTHER = "Ваше обращение отправленно специалисту."

# Константы проекта
RELOAD_TIME = 15
# noga - после падения, бот ждёт 15 сек до перезапуска
