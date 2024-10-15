from config.config import CONFIG
from util.global_logger import GLOBAL_LOGGER as LOG
from util.shutdown import shutdown

from data_scraping.collect_dactyl import collect_dactyl
from data_scraping.collect_categories import collect_categories
from data_scraping.annotation_cleanup import clean_annotations
from pose_estimation.estimate_poses import estimate_poses
from pose_estimation.fast_pose_annotation import fast_annotate
from pose_estimation.pose_postprocessing import pose_postprocessing

from translation.spoken_to_sign import spoken_to_sign

from functools import wraps


def retry_continue(func, retries=3, exceptions=(Exception,), *args, **kwargs):
    """
    Retry a function if it raises an exception.

    :param func: The function to retry
    :param retries: Number of retries before giving up (default is 3)
    :param exceptions: Tuple of exceptions to catch and retry on (default is all Exceptions)
    """

    attempt = 0
    while attempt < retries:
        try:
            return func(*args, **kwargs)
        except exceptions as e:
            attempt += 1
            LOG.error(f"Exception occurred: {e}. Retrying {attempt}/{retries}...")
            if attempt >= retries:
                LOG.error(f"Failed after {retries} attempts.")


def main():
    LOG.info('=' * 50 + 'DATA PREP APP START' + '=' * 50)
    if CONFIG.SCRAPING_ENABLED:
        collect_dactyl()
        collect_categories()
    if CONFIG.ANNOTATION_CLEANUP_ENABLED:
        clean_annotations()
    if CONFIG.POSE_ESTIMATION_ENABLED:
        estimate_poses()
        fast_annotate()
        if CONFIG.MERGE_POSES_TO_ONE_ARCHIVE:
            pose_postprocessing()
    if CONFIG.TRANSLATION_ENABLED:
        retry_continue(spoken_to_sign())

    LOG.info('=' * 51 + 'DATA PREP APP END' + '=' * 51 + '\n')

    if CONFIG.SYSTEM_SHUTDOWN_ON_END:
        shutdown()


if __name__ == '__main__':
    main()
