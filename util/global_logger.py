import sys
import logging
from logging.handlers import RotatingFileHandler

from config.config import CONFIG
from util.path_resolver import PATH_RESOLVER as REPATH


logging.basicConfig(
    level=CONFIG.LOG_LEVEL,
    format=CONFIG.LOG_FORMAT,  # Include filename
    handlers=[
        RotatingFileHandler(
            REPATH.LOG_DIR / 'project.log',
            maxBytes=CONFIG.LOG_FILE_SIZE,
            backupCount=CONFIG.LOG_FILE_COUNT,
            encoding='utf-8'
        ),
        logging.StreamHandler()
    ]
)

GLOBAL_LOGGER = logging.getLogger('ProjectLogger')

if CONFIG.LOG_EXCEPTIONS_FROM_ALL:
    def log_all_exceptions(exctype, value, tb):
        GLOBAL_LOGGER.error(f"Uncaught exception: {exctype.__name__}({value})", exc_info=(exctype, value, tb))

    sys.excepthook = log_all_exceptions
