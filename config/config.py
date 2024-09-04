import logging


class ProjectConfig:
    # ======================================== APP  OPTIONS ========================================
    LOG_LEVEL = logging.WARNING
    LOG_FORMAT = '%(asctime)s | %(levelname)10s | %(filename)30s:%(lineno)4s | %(funcName)30s() | %(message)s'
    LOG_FILE_SIZE = 1*1024*1024
    LOG_FILE_COUNT = 10
    REQUESTS_PER_SECOND = 3

    # ====================================== SCRAPING OPTIONS ======================================
    SITE_NAME = 'https://spreadthesign.com'     # don't change
    LANG_ALIAS = 'uk.ua'                        # change according to site aliases

    # don't change these two, unless you know what you're doing
    COOKIES = {'sts_preferences': f'{{"language_choice_message_shown": true, "last_choosen_language": "{LANG_ALIAS}", "show_more_languages": false}}'}
    HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)', 'Referer': 'https://spreadthesign.com/'}

    SKIP_TO_CATEGORY = None
    # TODO: check https://spreadthesign.com/uk.ua/search/by-category/28/mova/?q=&p=27


CONFIG = ProjectConfig()
