import logging
import sys
from logging.handlers import RotatingFileHandler

from constants import BACKUP_COUNT, ENCODING, FORMAT, LOGS_FOLDER, MAX_BYTES


def init_globals_logging():
    """Инициализация глобальных натсроек логера."""
    logging.basicConfig(
        format=FORMAT,
        handlers=[
            logging.StreamHandler(sys.stdout),
            RotatingFileHandler(LOGS_FOLDER, encoding=ENCODING,
                                maxBytes=MAX_BYTES, backupCount=BACKUP_COUNT)
        ]
    )
