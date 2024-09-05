from config.config import CONFIG
from util.global_logger import GLOBAL_LOGGER as log

from data_scraping.collect_dactyl import collect_dactyl
from data_scraping.collect_categories import collect_categories


def main():
    log.info('='*50 + 'APP START' + '='*50)
    if CONFIG.SCRAPING_ENABLED:
        collect_dactyl()
        collect_categories()
    log.info('='*51 + 'APP END' + '='*51 + '\n')


if __name__ == '__main__':
    main()
