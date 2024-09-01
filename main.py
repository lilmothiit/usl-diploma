import logging

from config.config import CONFIG as config
from config.global_logger import GLOBAL_LOGGER as log
from config.global_ratelimiter import GLOBAL_SESSION as sesh
from config.path_resolver import PATH_RESOLVER as repath

from data_scraping.collect_dactyl import collect_dactyl


def main():
    log.info('Program started')
    collect_dactyl()
    log.info('Program finished')


if __name__ == '__main__':
    main()
