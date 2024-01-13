import logging
import sys
from logging.handlers import RotatingFileHandler

from constants import BACKUP_COUNT, ENCODING, LOG_FILE_FOLDER, MAX_BYTES


def init_globals_logging():
    """Инициализация глобальных натсроек логера."""
    logging.basicConfig(
        format='%(asctime)s - %(levelname)s - %(message)s - %(name)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            RotatingFileHandler(LOG_FILE_FOLDER, encoding=ENCODING,
                                maxBytes=MAX_BYTES, backupCount=BACKUP_COUNT)
        ]
    )
