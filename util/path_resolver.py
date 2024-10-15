from pathlib import Path
from urllib.parse import urlparse, urljoin, parse_qs, urlencode, urlunparse
from config.config import CONFIG


class PathResolver:
    # site
    ALPHABET_PAGE = f'{CONFIG.SITE_NAME}/{CONFIG.LANG_ALIAS}/alphabet/'
    CATEGORY_PAGE = f'{CONFIG.SITE_NAME}/{CONFIG.LANG_ALIAS}/search/by-category/'

    # project paths
    PROJECT_ROOT = Path(__file__).resolve().parent.parent
    LOG_DIR = PROJECT_ROOT / 'logs'
    DATA_DIR = PROJECT_ROOT / 'data' / CONFIG.LANG_ALIAS

    ANNOTATION_DIR = DATA_DIR / 'annotation'
    RAW_DATA_DIR = DATA_DIR / 'raw'
    POSE_DATA_DIR = DATA_DIR / 'pose'
    DACTYL_RAW_DIR = RAW_DATA_DIR / 'dactyl'
    DACTYL_POSE_DIR = POSE_DATA_DIR / 'dactyl'
    WORD_RAW_DIR = RAW_DATA_DIR / 'words'
    WORD_POSE_DIR = POSE_DATA_DIR / 'words'

    LANG_DATASET_DIR = DATA_DIR / CONFIG.LANG_DATASET_DIR_NAME

    MODEL_DIR = PROJECT_ROOT / 'models' / CONFIG.LANG_ALIAS
    INTERPRETER_DIR = MODEL_DIR / 'interpreter'
    TRANSLATOR_DIR = MODEL_DIR / 'translator'

    def __init__(self):
        for attr in dir(self):
            if attr.endswith('_DIR'):
                getattr(self, attr).mkdir(parents=True, exist_ok=True)

    @staticmethod
    def resolve_relative_url(relative_url):
        return urljoin(CONFIG.SITE_NAME, relative_url)

    @staticmethod
    def update_url_query(site_url, new_query):
        parsed_url = urlparse(site_url)
        existing_query_params = parse_qs(parsed_url.query)
        new_query_params = parse_qs(new_query)
        existing_query_params.update(new_query_params)
        updated_query = urlencode(existing_query_params, doseq=True)
        updated_url = urlunparse((
            parsed_url.scheme,
            parsed_url.netloc,
            parsed_url.path,
            parsed_url.params,
            updated_query,
            parsed_url.fragment
        ))

        return updated_url

    @staticmethod
    def join_url_query(base_url, query_string):
        if not query_string.startswith('?'):
            query_string = '?' + query_string

        full_url = base_url + query_string
        return full_url

    def resolve_project_relative_path(self, absolute):
        return Path(absolute).relative_to(self.PROJECT_ROOT)

    @staticmethod
    def get_file_name(url):
        parsed_url = urlparse(url)
        return parsed_url.path.split('/')[-1]

    def exists(self, path):
        path = Path(path)
        if not path.is_absolute():
            path = self.PROJECT_ROOT / path
        return path.exists()


PATH_RESOLVER = PathResolver()

