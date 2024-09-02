import logging

from config.config import CONFIG as config
from config.global_logger import GLOBAL_LOGGER as log
from config.global_ratelimiter import GLOBAL_SESSION as sesh
from config.path_resolver import PATH_RESOLVER as repath

from data_scraping.collect_dactyl import collect_dactyl


def main():
    log.info('\n' + '='*50 + 'APP START' + '='*50)
    collect_dactyl()
    log.info('\n' + '='*51 + 'APP END' + '='*51 + '\n')


if __name__ == '__main__':
    main()
