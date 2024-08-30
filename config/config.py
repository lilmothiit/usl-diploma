import logging

class ProjectConfig:
    LOG_LEVEL = logging.DEBUG

    # ====================================== SCRAPING OPTIONS ======================================
    SITE_NAME = 'https://spreadthesign.com' # don't change
    LANG_ALIAS = 'uk.ua'                    # change according to site aliases
    SAVE_HTML = False                       # change according to preference, mainly used for debug

    # don't change these two, unless you know what you're doing
    COOKIES = {'sts_preferences':  f'{{"language_choice_message_shown": false, "last_choosen_language": "{LANG_ALIAS}", "show_more_languages": false}}'}
    HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)', 'Referer': 'https://spreadthesign.com/'}


CONFIG = ProjectConfig()
