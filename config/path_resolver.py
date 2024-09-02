from pathlib import Path
from urllib.parse import urlparse
from .config import CONFIG


class PathResolver:
    # site
    ALPHABET_PAGE = f'{CONFIG.SITE_NAME}/{CONFIG.LANG_ALIAS}/alphabet/'
    CATEGORY_PAGE = f'{CONFIG.SITE_NAME}/{CONFIG.LANG_ALIAS}/search/by-category/'

    # project paths
    PROJECT_ROOT = Path(__file__).resolve().parent.parent
    LOG_DIR = PROJECT_ROOT / 'logs'
    DATA_DIR = PROJECT_ROOT / 'data' / CONFIG.LANG_ALIAS
    DACTYL_DIR = DATA_DIR / 'dactyl'

    def __init__(self):
        self.LOG_DIR.mkdir(exist_ok=True)
        self.DATA_DIR.mkdir(exist_ok=True)
        self.DACTYL_DIR.mkdir(exist_ok=True)

    @staticmethod
    def resolve_relative_url(relative_url):
        return urlparse(CONFIG.SITE_NAME, relative_url)


PATH_RESOLVER = PathResolver()

