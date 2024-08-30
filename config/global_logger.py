import logging
from logging.handlers import RotatingFileHandler
from .config import CONFIG
from .path_resolver import PATH_RESOLVER as repath


logging.basicConfig(
    level=logging.DEBUG,
    format='%(filename)s | %(levelname)s | %(message)s',  # Include filename
    handlers=[
        RotatingFileHandler(
            repath.LOG_DIR / 'project.log',
            maxBytes=20000,
            backupCount=10
        ),
        logging.StreamHandler()
    ]
)

GLOBAL_LOGGER = logging.getLogger('ProjectLogger')
GLOBAL_LOGGER.setLevel(CONFIG.LOG_LEVEL)