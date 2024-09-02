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

    contents = request_page_contents(page, tag='ul', tag_class='alphabet-letter-list')
    if not contents:
        LOG.warning('No alphabet found')
        return

    for a in contents.find_all('a', href=True):
        LOG.info(f'Scraping "{a.text.strip()}" : {a["href"]}')
        video_div = request_page_contents(REPATH.resolve_relative_url(a['href']),
                                          tag='div', tag_class='alphabet-letter-video')
        if not video_div:
            LOG.warning(f'Failed to collect video from "{a.text.strip()}" : {a["href"]}')
            continue

        video_src = video_div.find('video')['src']

        #a.text
        #a['href']


if __name__ == '__main__':
    collect_dactyl()
