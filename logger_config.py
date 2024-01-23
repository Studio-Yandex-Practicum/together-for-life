"""Модуль инициализации глобальных натсроек логера."""

import logging
import os
import sys
from logging.handlers import RotatingFileHandler

from constants import (
    BACKUP_COUNT,
    DATE_FORMAT,
    ENCODING,
    FORMAT,
    LOGS_FILE,
    LOGS_FOLDER,
    MAX_BYTES,
)


def init_globals_logging():
    """Инициализация глобальных натсроек логера."""
    os.makedirs(LOGS_FOLDER, exist_ok=True)
    logging.basicConfig(
        format=FORMAT,
        datefmt=DATE_FORMAT,
        handlers=[
            logging.StreamHandler(sys.stdout),
            RotatingFileHandler(
                os.path.join(LOGS_FOLDER, LOGS_FILE),
                encoding=ENCODING,
                maxBytes=MAX_BYTES,
                backupCount=BACKUP_COUNT,
            ),
        ],
    )
