from util.global_logger import GLOBAL_LOGGER as LOG
from util.path_resolver import PATH_RESOLVER as REPATH

from data_scraping.scraping_util import request_page_contents, scrape_file
from util.annotator import Annotator

def find_all_video(soup, tag, tag_class, tag_id):
    pass


def scrape_page(url, *args):
    LOG.info(f'Collecting from {url}')

    words_list = request_page_contents(url, *args)
    if not words_list:
        LOG.error('Requested content not found')
        return

    for a in words_list.find_all('a', href=True):
        LOG.info(f'Scraping "{a.text.strip()}" at {a["href"]}')
        word_content = request_page_contents(a['href'])

