from config.config import CONFIG
from util.global_logger import GLOBAL_LOGGER as log

from data_scraping.collect_dactyl import collect_dactyl
from data_scraping.collect_categories import collect_categories
from data_scraping.annotation_cleanup import clean_annotations
from pose_estimation.pose_estimation import pose_estimation


def main():
    log.info('='*50 + 'APP START' + '='*50)
    if CONFIG.SCRAPING_ENABLED:
        collect_dactyl()
        collect_categories()
    if CONFIG.ANNOTATION_CLEANUP_ENABLED:
        clean_annotations()
    if CONFIG.POSE_ESTIMATION_ENABLED:
        pose_estimation()
    log.info('='*51 + 'APP END' + '='*51 + '\n')


if __name__ == '__main__':
    main()
