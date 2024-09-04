import logging


class ProjectConfig:
    # ======================================== APP  OPTIONS ========================================
    LOG_LEVEL = logging.INFO
    LOG_FORMAT = '%(asctime)s | %(filename)s | %(levelname)s | %(message)s'
    REQUESTS_PER_SECOND = 5

    # ====================================== SCRAPING OPTIONS ======================================
    SITE_NAME = 'https://spreadthesign.com'     # don't change
    LANG_ALIAS = 'uk.ua'                        # change according to site aliases

    # don't change these two, unless you know what you're doing
    COOKIES = {'sts_preferences': f'{{"language_choice_message_shown": true, "last_choosen_language": "{LANG_ALIAS}", "show_more_languages": false}}'}
    HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)', 'Referer': 'https://spreadthesign.com/'}


CONFIG = ProjectConfig()
