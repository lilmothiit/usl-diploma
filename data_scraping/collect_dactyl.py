from util.global_logger import GLOBAL_LOGGER as LOG
from util.path_resolver import PATH_RESOLVER as REPATH

from util.scraping import request_page_contents, scrape_file
from util.annotator import Annotator



def collect_dactyl():
    page = REPATH.ALPHABET_PAGE
    LOG.info('Collecting alphabet from ' + page)

    contents = request_page_contents(page, tag='ul', tag_class='alphabet-letter-list')
    if not contents:
        LOG.error('No alphabet found')
        return

    annotator = Annotator(REPATH.ANNOTATION_DIR / 'dactyl.csv')

    for a in contents.find_all('a', href=True):
        LOG.info(f'Scraping "{a.text.strip()}" at {a["href"]}')
        video_div = request_page_contents(REPATH.resolve_relative_url(a['href']),
                                          tag='div', tag_class='alphabet-letter-video')
        if not video_div:
            LOG.warning(f'Failed to collect video from "{a.text.strip()}" : {a["href"]}')
            continue

        video_src = video_div.find('video')['src']
        output_abs_path = REPATH.DACTYL_DIR / REPATH.get_file_name(video_src)
        output_rel_path = REPATH.resolve_project_relative_path(output_abs_path)

        if REPATH.exists(output_abs_path):
            LOG.info(f'file {output_rel_path} already exists')
            continue

        scrape_file(video_src, output_abs_path)
        annotator.record(line=[a.text.strip(), None, 'dactyl', video_src, output_rel_path])


