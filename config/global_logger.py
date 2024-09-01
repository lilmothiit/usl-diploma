import logging
from logging.handlers import RotatingFileHandler

from .config import CONFIG
from .path_resolver import PATH_RESOLVER as REPATH


logging.basicConfig(
    level=CONFIG.LOG_LEVEL,
    format=CONFIG.LOG_FORMAT,  # Include filename
    handlers=[
        RotatingFileHandler(
            REPATH.LOG_DIR / 'project.log',
            maxBytes=20000,
            backupCount=10
        ),
        logging.StreamHandler()
    ]
)

GLOBAL_LOGGER = logging.getLogger('ProjectLogger')
