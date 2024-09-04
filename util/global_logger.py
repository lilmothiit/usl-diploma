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
