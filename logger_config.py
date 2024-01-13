import logging
import sys
from logging.handlers import RotatingFileHandler


def init_globals_logging():
    """Инициализация глобальных натсроек логера."""
    logging.basicConfig(
        format='%(asctime)s - %(levelname)s - %(message)s - %(name)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            RotatingFileHandler('logs/logfile.log', encoding='cp1251',
                                maxBytes=50000000, backupCount=5)
        ]
    )
