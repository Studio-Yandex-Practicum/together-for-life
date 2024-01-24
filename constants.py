# Глобальные настройки логера
BACKUP_COUNT = 5
ENCODING = "UTF-8"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
FORMAT = "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
LOGGING_LEVEL = "DEBUG"
LOGS_FOLDER = "logs"
LOGS_FILE = "logfile.log"
LOGGER_NAME = "vk-bot"
MAX_BYTES = 50_000_000

# Константы ВК чат-бота
ECHO_MESSAGE_TEMPLATE = "Поступило сообщение: {}."
CHECKING_UNIQUE = 0
# 0 — проверка на уникальность не нужна.
# Любое другое число в пределах int32 — проверка на уникальность нужна.

# Константы проекта
RELOAD_TIME = 15
# noga - после падения, бот ждёт 15 сек до перезапуска
