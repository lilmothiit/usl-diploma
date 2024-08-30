from pathlib import Path
from .config import CONFIG

class PathResolver:
    # site
    ALPHABET_PAGE = f'{CONFIG.SITE_NAME}/{CONFIG.LANG_ALIAS}/alphabet/'

    # project paths
    PROJECT_ROOT = Path(__file__).resolve().parent.parent
    LOG_DIR = PROJECT_ROOT / 'logs'
    DATA_DIR = PROJECT_ROOT / 'data' / CONFIG.LANG_ALIAS
    DACTYL_DIR = DATA_DIR / 'dactyl'

    def __init__(self):
        self.LOG_DIR.mkdir(exist_ok=True)
        self.DATA_DIR.mkdir(exist_ok=True)
        self.DACTYL_DIR.mkdir(exist_ok=True)

PATH_RESOLVER = PathResolver()

