from util.global_logger import GLOBAL_LOGGER as LOG
from util.path_resolver import PATH_RESOLVER as REPATH

from data_scraping.scraping_util import request_page_contents, scrape_file
from util.annotator import Annotator


def collect_categories():
    page = REPATH.CATEGORY_PAGE
    LOG.info('Collecting category list')

    contents = request_page_contents(page, tag='ul', tag_id='categories')
    if not contents:
        LOG.error('No list found')
        return

    # annotator = Annotator(REPATH.ANNOTATION_DIR / 'words.csv')


