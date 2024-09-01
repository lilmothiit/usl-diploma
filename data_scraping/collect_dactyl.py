import os
from bs4 import BeautifulSoup

from config.config import CONFIG
from config.global_logger import GLOBAL_LOGGER as LOG
from config.global_ratelimiter import GLOBAL_SESSION as SESH
from config.path_resolver import PATH_RESOLVER as REPATH

from util.scraping import request_page_contents



def collect_dactyl():
    page = REPATH.ALPHABET_PAGE
    LOG.info('Collecting alphabet from ' + page)

    contents = request_page_contents(page)

    for a in contents.find_all('a', href=True):
        pass
        #a.text
        #a['href']


if __name__ == '__main__':
    collect_dactyl()
