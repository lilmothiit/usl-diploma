import logging
from mediapipe import solutions
from mediapipe.tasks.python import BaseOptions
from mediapipe.tasks.python.vision.core.vision_task_running_mode import VisionTaskRunningMode
import config.pose_styles as pose_styles


class ProjectConfig:
    # ================================================== APP  OPTIONS ==================================================
    LOG_LEVEL = logging.INFO
    LOG_EXCEPTIONS_FROM_ALL = True
    LOG_FORMAT = '%(asctime)s | %(levelname)10s | %(filename)30s:%(lineno)4s | %(funcName)30s() | %(message)s'
    LOG_FILE_SIZE = 2*1024*1024
    LOG_FILE_COUNT = 10
    REQUESTS_PER_SECOND = 5

    SYSTEM_SHUTDOWN_ON_END = False

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
    POSE_ESTIMATION_ENABLED = False         # whether to perform any pose estimation tasks at all
    POSE_ESTIMATION_OPTIONS = {
        'base_options': BaseOptions(
            model_asset_path='D:/Lin KPI/diploma/usl-diploma/models/holistic/holistic_landmarker.task'),
        'running_mode': VisionTaskRunningMode.VIDEO,    # don't change
        'min_face_detection_confidence' : 0.4,
        'min_face_suppression_threshold': 0.5,
        'min_face_landmarks_confidence' : 0.9,
        'min_pose_detection_confidence' : 0.9,
        'min_pose_suppression_threshold': 0.5,
        'min_pose_landmarks_confidence' : 0.9,
        'min_hand_landmarks_confidence' : 0.9,
        'output_face_blendshapes'       : True,
    }
    POSE_ESTIMATION_SOURCE = {
        'dactyl': False,
        'words': True
    }

    VIDEO_ANNOTATION_ENABLED = False    # whether to save annotated videos
    FORCE_VIDEO_ANNOTATION = True       # force video annotation, even if the respective annotated video already exists
    VIDEO_ANNOTATION_STYLES = (
        ('pose_landmarks', solutions.pose.POSE_CONNECTIONS, pose_styles.get_pose_landmarks_style()),
        ('face_landmarks', solutions.face_mesh_connections.FACEMESH_CONTOURS, None, pose_styles.get_face_mesh_contours_style()),
        ('left_hand_landmarks', solutions.hands_connections.HAND_CONNECTIONS, None, pose_styles.get_hand_connections_style()),
        ('right_hand_landmarks', solutions.hands_connections.HAND_CONNECTIONS, None, pose_styles.get_hand_connections_style())
    )

    POSE_ANNOTATION_ENABLED = True      # whether to save pose landmarks
    FORCE_POSE_ANNOTATION = True        # force pose estimation, even if the respective annotation file already exists
    REDUCE_POSE_PRECISION = None        # None or int to pass to the round function
    MERGE_POSES_TO_ONE_ARCHIVE = True   # compress all pose annotations to one list of pose annotation lists

    SELECTED_POSE_ANNOTATIONS = {       # only selected annotations will be saved
        'face_blendshapes'              : True,
        'face_landmarks'                : False,
        'pose_landmarks'                : False,
        'pose_world_landmarks'          : True,
        'left_hand_landmarks'           : False,
        'left_hand_world_landmarks'     : True,
        'right_hand_landmarks'          : False,
        'right_hand_world_landmarks'    : True,
    }

    POSE_ANNOTATION_FILE_TYPES = {      # annotations are written to each selected file type
        '.json'     : False,
        '.json.pkl' : False,
        '.csv'      : False,
        '.csv.pkl'  : True
    }

    # ================================================== TRANSLATION ==================================================
    TRANSLATION_ENABLED = True
    SPACY_MODEL_NAME = 'uk_core_news_trf'
    LANG_DATASET_DIR_NAME = 'ubertext'

    # ================================================= MODEL TRAINING =================================================
    TRAIN_INTERPRETER = False
    LOAD_INTERPRETER_CHECKPOINT = True
    
    INTERPRETER_EMBEDDING_DIM = 256
    INTERPRETER_HIDDEN_DIM = 128


CONFIG = ProjectConfig()
