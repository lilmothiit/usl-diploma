from bs4 import BeautifulSoup

from config.config import CONFIG
from util.global_logger import GLOBAL_LOGGER as LOG
from util.global_ratelimiter import GLOBAL_SESSION as SESH


def request_page_contents(url, tag=None, tag_class=None, output_file=None):
    """
    Requests the given URL. Returns a BeautifulSoup of the page.
    If the tag is specified, the soup is narrowed down to the first instance of that tag.
    If CONFIG.SAVE_HTML is set to True and html_save_path is specified,
    the processed soup is saved at html_save_path.

    :param url:         URL to request.
    :param tag:         (OPTIONAL) The tag to retrieve from the soup.
    :param tag_class:   (OPTIONAL) The class of the tag to retrieve from the soup.
                        If not specified, the tag search will disregard the tag class.
    :param output_file: (OPTIONAL) The path where the page will be saved.
    :return:            None | BeautifulSoup
    """
    response = SESH.get(url, headers=CONFIG.HEADERS, cookies=CONFIG.COOKIES)
    if response.status_code != 200:
        LOG.warning(f'Failed to fetch page {url}')
        return

    soup = BeautifulSoup(response.content, 'html.parser')

    if tag is None:
        return soup

    contents = soup.find(tag, class_=tag_class)
    if not contents:
        LOG.warning(f'Failed to find tag <{tag}> of class "{tag_class}" for {url}')
        return

    if CONFIG.SAVE_HTML and output_file is not None:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(str(contents.prettify()))
        LOG.info(f'Saved response to {output_file}')

    return contents


def scrape_file(src, output_file):
    response = SESH.get(src, headers=CONFIG.HEADERS, cookies=CONFIG.COOKIES)
    if response.status_code != 200:
        LOG.warning(f'Failed to fetch video from {src}')
        return

    with open(output_file, 'wb') as file:
        # Write the content of the response to the file in chunks
        for chunk in response.iter_content(chunk_size=8192):
            file.write(chunk)
        LOG.info(f'Saved video to {output_file}')
