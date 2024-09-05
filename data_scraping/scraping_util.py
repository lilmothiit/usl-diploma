from bs4 import BeautifulSoup

from config.config import CONFIG
from util.global_logger import GLOBAL_LOGGER as LOG
from util.global_ratelimiter import GLOBAL_SESSION as SESH


def request_page(url):
    """
    Requests the given URL. Returns a BeautifulSoup of the page.

    :param url:         URL to request.
    :return:            None | BeautifulSoup
    """
    response = SESH.get(url, headers=CONFIG.HEADERS, cookies=CONFIG.COOKIES)
    if response.status_code != 200:
        LOG.warning(f'Failed to fetch page {url}')
        return

    content_type = response.headers.get('Content-Type')
    if content_type:
        # Check if 'charset' is specified in the Content-Type header
        content_type_parts = content_type.split('charset=')
        if len(content_type_parts) > 1:
            # Set the encoding to the server-specified charset
            server_encoding = content_type_parts[1].strip()
            response.encoding = server_encoding
        else:
            # Fallback to apparent encoding if charset isn't specified
            response.encoding = response.apparent_encoding
    else:
        # Fallback to apparent encoding if no Content-Type header is available
        response.encoding = response.apparent_encoding

    soup = BeautifulSoup(response.content.decode(response.encoding, errors='replace'), 'html.parser')
    return soup


def request_page_contents(url, tag=None, tag_class=None, tag_id=None):
    """
    Requests the given URL. Returns a BeautifulSoup of the page.
    If the tag is specified, the soup is narrowed down to the first instance of that tag.

    :param url:         URL to request.
    :param tag:         (OPTIONAL) The tag to retrieve from the soup.
    :param tag_class:   (OPTIONAL) The class of the tag to retrieve from the soup.
                        If not specified, the tag search will disregard the tag class.
                        If specified without specifying the tag, has no effect.
    :param tag_id:      (OPTIONAL) The ID of the tag to retrieve from the soup.
                        If not specified, the tag search will disregard the tag id.
                        If specified without specifying the tag, has no effect.
    :return:            None | BeautifulSoup
    """
    response = SESH.get(url, headers=CONFIG.HEADERS, cookies=CONFIG.COOKIES)
    if response.status_code != 200:
        LOG.warning(f'Failed to fetch page {url}')
        return

    content_type = response.headers.get('Content-Type')
    if content_type:
        # Check if 'charset' is specified in the Content-Type header
        content_type_parts = content_type.split('charset=')
        if len(content_type_parts) > 1:
            # Set the encoding to the server-specified charset
            server_encoding = content_type_parts[1].strip()
            response.encoding = server_encoding
        else:
            # Fallback to apparent encoding if charset isn't specified
            response.encoding = response.apparent_encoding
    else:
        # Fallback to apparent encoding if no Content-Type header is available
        response.encoding = response.apparent_encoding

    soup = BeautifulSoup(response.content.decode(response.encoding, errors='replace'), 'html.parser')

    if tag is None:
        return soup

    attrs = {}
    if tag_class:
        attrs['class'] = tag_class
    if tag_id:
        attrs['id'] = tag_id

    contents = soup.find(tag, attrs=attrs, recursive=True)
    if not contents:
        LOG.warning(f'Failed to find tag <{tag}> of class "{tag_class}" and id "{tag_id}" at {url}')
        return

    return contents


def scrape_file(src, output_file):
    response = SESH.get(src, headers=CONFIG.HEADERS, cookies=CONFIG.COOKIES)
    if response.status_code != 200:
        LOG.warning(f'Failed to fetch file from {src}')
        return

    with open(output_file, 'wb') as file:
        # Write the content of the response to the file in chunks
        for chunk in response.iter_content(chunk_size=8192):
            file.write(chunk)
        LOG.info(f'Saved file to {output_file}')
