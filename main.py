from config.config import CONFIG
from util.global_logger import GLOBAL_LOGGER as log

from data_scraping.collect_dactyl import collect_dactyl
from data_scraping.collect_categories import collect_categories
from data_scraping.annotation_cleanup import clean_annotations
from pose_estimation.estimate_poses import estimate_poses
from pose_estimation.fast_pose_annotation import fast_annotate


def main():
    log.info('='*50 + 'APP START' + '='*50)
    if CONFIG.SCRAPING_ENABLED:
        collect_dactyl()
        collect_categories()
    if CONFIG.ANNOTATION_CLEANUP_ENABLED:
        clean_annotations()
    if CONFIG.POSE_ESTIMATION_ENABLED:
        estimate_poses()
        fast_annotate()

    log.info('='*51 + 'APP END' + '='*51 + '\n')


if __name__ == '__main__':
    main()
