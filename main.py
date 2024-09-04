from util.global_logger import GLOBAL_LOGGER as log

from data_scraping.collect_dactyl import collect_dactyl
from data_scraping.collect_categories import collect_categories


def main():
    log.info('\n' + '='*50 + 'APP START' + '='*50)
    collect_dactyl()
    collect_categories()
    log.info('\n' + '='*51 + 'APP END' + '='*51 + '\n')


if __name__ == '__main__':
    main()
