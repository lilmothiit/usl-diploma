from config.config import CONFIG

from util.global_logger import GLOBAL_LOGGER as LOG
from util.path_resolver import PATH_RESOLVER as REPATH

from data_scraping.scraping_util import request_page_contents, scrape_file
from util.annotator import Annotator


def find_all_videos(soup):
    video_tag = soup.find('video', recursive=True)
    if video_tag is None:
        return
    video_column = video_tag.parent
    nav_bar = video_column.find('ul', class_='nav')

    if not nav_bar:
        return [video_tag['src']]

    video_srcs = []
    for a in nav_bar.find_all('a', href=True):
        video = request_page_contents(REPATH.resolve_relative_url(a['href']), tag='video')
        if not video:
            continue
        video_src = video['src']
        video_srcs.append(video_src)

    return video_srcs


def scrape_category_page(url, category, annotator):
    LOG.info(f'Collecting from {url}')

    words_list = request_page_contents(url, tag='div', tag_class='search-results')
    if not words_list:
        LOG.error(f'Content list not found: {url}')
        return

    for div in words_list.find_all('div', class_='search-result'):
        a = div.find('a', href=True)
        word = a.contents[0].strip()
        part_of_speech = a.find('small')
        if part_of_speech:
            part_of_speech = part_of_speech.text.strip()
        word_link = a["href"]
        LOG.info(f'Scraping "{word}" ({part_of_speech}) at {word_link}')

        word_content = request_page_contents(REPATH.resolve_relative_url(word_link),
                                             tag='div', tag_class='search-result-content')
        if not word_content:
            LOG.warning(f'Search result content not found for "{word}" ({part_of_speech}) at {word_link}')
            continue

        video_srcs = find_all_videos(word_content)
        if not video_srcs:
            LOG.warning(f'No video sources found for "{word}" ({part_of_speech}) at {word_link}')
            continue

        for video_src in video_srcs:
            output_abs_path = REPATH.WORD_RAW_DIR / REPATH.get_file_name(video_src)
            output_rel_path = REPATH.resolve_project_relative_path(output_abs_path)
            annotator.record(line=[word, part_of_speech, category, video_src, output_rel_path])

            if REPATH.exists(output_abs_path):
                LOG.info(f'File {output_rel_path} already exists')
            else:
                scrape_file(video_src, output_abs_path)

    return words_list


def category_scraper(start_page, skip_to_page, *args):
    if skip_to_page:
        url = REPATH.join_url_query(start_page, f'p={skip_to_page}')
    else:
        url = start_page

    while True:
        search_result = scrape_category_page(url, *args)
        pager = search_result.find('div', class_='search-pager-next', recursive=True)
        if not pager:
            LOG.warning(f'Pager not found at {url}')
            break
        a = pager.find('a')
        if not a:
            LOG.info(f'Next page query not found at {url}, category scraping assumed complete')
            break
        query = a['href']
        url = REPATH.join_url_query(start_page, query)


def collect_categories():
    LOG.info('Collecting category list')

    page = REPATH.CATEGORY_PAGE
    unordered_list = request_page_contents(page, tag='ul', tag_id='categories')
    if not unordered_list:
        LOG.error('No list found')
        return

    LOG.info('Initiating word scraping')
    annotator = Annotator(REPATH.ANNOTATION_DIR / 'words.csv')

    skip_page = CONFIG.RESUME_FROM_CATEGORY_PAGE
    for li in unordered_list.find_all('li'):
        a = li.find('a', href=True)
        category = a.text.strip()
        start_page = REPATH.resolve_relative_url(a['href'])

        # if we haven't skipped yet, need to skip, and the current category is wrong -> skip
        if skip_page and CONFIG.RESUME_FROM_CATEGORY and CONFIG.RESUME_FROM_CATEGORY != category:
            LOG.info(f'Skipping "{category}" at {start_page})')
            continue

        # if we found the specified category and used the page number, unset it, stopping the skipping
        if CONFIG.RESUME_FROM_CATEGORY == category:
            LOG.info(f'Starting word scraping for "{category}" (page {skip_page}) at {start_page}')
            category_scraper(start_page, skip_page, category, annotator)
            skip_page = None
            continue

        # in all other cases, scrape normally
        LOG.info(f'Starting word scraping for "{category}" at {start_page}')
        category_scraper(start_page, None, category, annotator)
