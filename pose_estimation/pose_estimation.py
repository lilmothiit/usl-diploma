import cv2
import pandas as pd
import mediapipe.python.solutions.drawing_utils as mp_drawing
import mediapipe.python.solutions.drawing_styles as mp_drawing_styles
import mediapipe.python.solutions.holistic as mp_holistic

from config.config import CONFIG
from util.global_logger import GLOBAL_LOGGER as LOG
from util.path_resolver import PATH_RESOLVER as REPATH

import warnings
warnings.filterwarnings("ignore", module='mediapipe')
warnings.filterwarnings("ignore", module='tensorflow')

_HOLISTIC_ARGS = {
    'static_image_mode': False,
    'model_complexity': 2,
    'min_detection_confidence': 0.9,
    'min_tracking_confidence': 0.9
}
_ANNOTATION_STYLES = {
    'pose_landmarks': (mp_holistic.POSE_CONNECTIONS, mp_drawing_styles.get_default_pose_landmarks_style()),
    'face_landmarks': (mp_holistic.FACEMESH_TESSELATION, mp_drawing_styles.get_default_face_mesh_tesselation_style()),
    'left_hand_landmarks': (mp_holistic.HAND_CONNECTIONS, mp_drawing_styles.get_default_hand_landmarks_style()),
    'right_hand_landmarks': (mp_holistic.HAND_CONNECTIONS, mp_drawing_styles.get_default_hand_landmarks_style())
}


def draw_annotation(image, annotation):
    # Draw landmark annotation on the image.
    image.flags.writeable = True
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    for annot_type, style in _ANNOTATION_STYLES.items():
        annot = getattr(annotation, annot_type)
        if not annot:
            continue
        mp_drawing.draw_landmarks(image, annot, *style)

    return image


def holistic_process(input_, output):
    LOG.info(f'Processing video {input_}')
    in_vid = cv2.VideoCapture(input_)

    out_vid = None
    if output:
        frame_width = int(in_vid.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(in_vid.get(cv2.CAP_PROP_FRAME_HEIGHT))
        frame_rate = int(in_vid.get(cv2.CAP_PROP_FPS))
        fourcc = cv2.VideoWriter.fourcc(*'mp4v')
        out_vid = cv2.VideoWriter(output, fourcc, frame_rate, (frame_width, frame_height))

    if not in_vid.isOpened():
        LOG.error(f"Error opening video file {input_}")
        return

    results = []
    with mp_holistic.Holistic(_HOLISTIC_ARGS) as holistic:
        while in_vid.isOpened():
            success, image = in_vid.read()
            if not success:
                LOG.info("Reached end of video")
                break

            # To improve performance, optionally mark the image as not writeable to pass by reference.
            image.flags.writeable = False
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            results.append(holistic.process(image))

            if out_vid is not None:
                image = draw_annotation(image, results[-1])
                out_vid.write(image)

    in_vid.release()
    out_vid.release()
    return results


def pose_estimation():
    df = pd.read_csv(REPATH.ANNOTATION_DIR / 'dactyl.csv', delimiter=';')

    out_video_path = None
    for path in df['local_path']:
        in_path = REPATH.PROJECT_ROOT / path

        if CONFIG.VIDEO_ANNOTATION_ENABLED:
            out_video_path = REPATH.DACTYL_POSE_DIR / in_path.name
            if REPATH.exists(out_video_path):
                LOG.info(f"Video already exists: {out_video_path}")
                if not CONFIG.FORCE_VIDEO_ANNOTATION:
                    out_video_path = None

        result = holistic_process(in_path, out_video_path)
        if result is None:
            continue



if __name__ == '__main__':
    pose_estimation()
