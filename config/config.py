import logging


class ProjectConfig:
    # ================================================== APP  OPTIONS ==================================================
    LOG_LEVEL = logging.INFO
    LOG_EXCEPTIONS_FROM_ALL = True
    LOG_FORMAT = '%(asctime)s | %(levelname)10s | %(filename)30s:%(lineno)4s | %(funcName)30s() | %(message)s'
    LOG_FILE_SIZE = 2*1024*1024
    LOG_FILE_COUNT = 10
    REQUESTS_PER_SECOND = 5

    # ================================================ SCRAPING OPTIONS ================================================
    SCRAPING_ENABLED = False                    # whether to perform data scraping
    ANNOTATION_CLEANUP_ENABLED = False          # whether to perform annotation cleanup
    SITE_NAME = 'https://spreadthesign.com'     # don't change
    LANG_ALIAS = 'uk.ua'                        # change according to site aliases

    # don't change these two, unless you know what you're doing
    COOKIES = {'sts_preferences': f'{{"language_choice_message_shown": true, \
                                      "last_choosen_language": "{LANG_ALIAS}", \
                                      "show_more_languages": false}}'}
    HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)', 'Referer': 'https://spreadthesign.com/'}

    # resuming from a category also skips dactyl scraping
    RESUME_FROM_CATEGORY = None         # category name from the category page (e.g. "Numbers", "Language" etc.)
    RESUME_FROM_CATEGORY_PAGE = None    # integer page number

    # ================================================ POSE  ESTIMATION ================================================
    POSE_ESTIMATION_ENABLED = True      # whether to perform any pose estimation tasks at all
    POSE_ANNOTATION_ENABLED = True      # whether to save pose landmarks
    FORCE_POSE_ANNOTATION = True        # force pose estimation, even if the respective annotation file already exists
    VIDEO_ANNOTATION_ENABLED = True     # whether to save annotated videos
    FORCE_VIDEO_ANNOTATION = True      # force video annotation, even if the respective annotated video already exists
    POSE_ESTIMATION_OPTIONS = {
        'static_image_mode'         : False,    # whether input is treated as static images or stream
        'model_complexity'          : 2,        # one of [0, 1, 2] with higher value giving better results
        'smooth_landmarks'          : True,     # whether to reduce jitter
        'enable_segmentation'       : False,    # whether to find ROI of the detected person
        'smooth_segmentation'       : True,     # whether to reduce jitter of the ROI
        'refine_face_landmarks'     : True,     # whether to refine landmarks and detect irises (+10 landmarks)
                                                # NOTE that refinement can fail, and iris landmarks will not exist
        'min_detection_confidence'  : 0.9,      # [0.0, 1.0] minimum confidence value of the person-detection model
        'min_tracking_confidence'   : 0.9       # [0.0, 1.0] minimum confidence value of the pose-detection models
    }

    REDUCE_POSE_PRECISION = False       # False to avoid rounding or ndigit value for the round() function
    REDUCE_FACE_MESH = True             # If true, out of all 468-478 landmarks, only selected categories are saved
    SELECT_FACE_PARTS = {
        'face_outline',
        'lips_inside',
        'lips_outside',
        'nose_tip',
        # 'nose_tip_extended',  # selects both the tip and 4 cardinally connected vertices
        'left_eye',
        'right_eye',
        'left_iris',            # refine_face_landmarks needs to be True
        'right_iris',           # refine_face_landmarks needs to be True
        'left_eyebrow',
        'right_eyebrow',
    }
    POSE_ANNOTATION_TYPES = {   # annotations are written to each selected file type
        '.json': False,
        '.msgpack.gz': True
    }


CONFIG = ProjectConfig()
