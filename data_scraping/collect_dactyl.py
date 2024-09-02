from util.global_logger import GLOBAL_LOGGER as LOG
from util.path_resolver import PATH_RESOLVER as REPATH

from util.scraping import request_page_contents, scrape_video
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
        LOG.info(f'Scraping "{a.text.strip()}" : {a["href"]}')
        video_div = request_page_contents(REPATH.resolve_relative_url(a['href']),
                                          tag='div', tag_class='alphabet-letter-video')
        if not video_div:
            LOG.warning(f'Failed to collect video from "{a.text.strip()}" : {a["href"]}')
            continue

        video_src = video_div.find('video')['src']
        output_path = REPATH.DACTYL_DIR / REPATH.resolve_file_name(video_src)
        output_rel_path = REPATH.resolve_project_relative_path(output_path)
        scrape_video(video_src, output_path)
        annotator.record(line=[a.text.strip(), 'dactyl', video_src, output_rel_path])


if __name__ == '__main__':
    collect_dactyl()
