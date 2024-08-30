import os
import json
from bs4 import BeautifulSoup

from config.config import CONFIG as config
from config.global_logger import GLOBAL_LOGGER as log
from config.global_ratelimiter import GLOBAL_SESSION as sesh
from config.path_resolver import PATH_RESOLVER as repath


def collect_dactyl():
    page = repath.ALPHABET_PAGE
    log.info('Collecting manual alphabet from ' + page)

    response = sesh.get(page, headers=config.HEADERS, cookies=config.COOKIES)
    if response.status_code != 200:
        log.warning('Failed to fetch manual alphabet page')
        return

    soup = BeautifulSoup(response.content, 'html.parser')
    contents = soup.find('div', class_='mw-parser-output')

    if not contents:
        log.warning(f'Failed to find manual alphabet page contents')
        return

    if config.SAVE_HTML:
        with open(os.path.join(repath.DACTYL_DIR, 'page_output.html'), 'w', encoding='utf-8') as f:
            f.write(str(contents.prettify()))
        log.info('Saved HTML')


if __name__ == '__main__':
    collect_dactyl()