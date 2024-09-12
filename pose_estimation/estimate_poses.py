import os
import cv2

import pandas as pd
import mediapipe.python.solutions.drawing_utils as mp_drawing
import mediapipe.python.solutions.drawing_styles as mp_drawing_styles
import mediapipe.python.solutions.holistic as mp_holistic

from config.config import CONFIG
from util.global_logger import GLOBAL_LOGGER as LOG
from util.path_resolver import PATH_RESOLVER as REPATH

if __name__ == '__main__':
    from pose_scribe import pose_scribe
else:
    from pose_estimation.pose_scribe import pose_scribe

import warnings
warnings.filterwarnings("ignore", message="Feedback manager requires a model with a single signature inference.")
warnings.filterwarnings("ignore", module='mediapipe')
warnings.filterwarnings("ignore", module='tensorflow')
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

_HOLISTIC_ARGS = CONFIG.POSE_ESTIMATION_OPTIONS
_ANNOTATION_STYLES = {
    'pose_landmarks': (mp_holistic.POSE_CONNECTIONS, mp_drawing_styles.get_default_pose_landmarks_style()),
    'face_landmarks': (mp_holistic.FACEMESH_CONTOURS, None, mp_drawing_styles.get_default_face_mesh_contours_style()),
    'left_hand_landmarks': (mp_holistic.HAND_CONNECTIONS, mp_drawing_styles.get_default_hand_landmarks_style()),
    'right_hand_landmarks': (mp_holistic.HAND_CONNECTIONS, mp_drawing_styles.get_default_hand_landmarks_style())
}

_SELECTED_FACE_VERTICES = {
    'face_outline':         [10, 338, 297, 332, 284, 251, 389, 356, 454, 323, 361, 288, 397, 365, 378, 400, 377,
                             152, 148, 176, 149, 150, 136, 172, 58, 132, 93, 234, 127, 162, 21, 54, 103, 67, 109],
    'lips_inside':          [13, 312, 311, 310, 415, 308, 324, 318, 402, 317, 14, 87, 178, 88, 95, 78, 191, 80, 81, 82],
    'lips_outside':         [0, 267, 269, 270, 409, 291, 375, 321, 405, 314, 17, 84, 181, 91, 146, 61, 185, 40, 39, 37],
    'nose_tip':             [4],
    'nose_tip_extended':    [1, 4, 5, 45, 275],
    'left_eye':             [133, 155, 154, 153, 145, 144, 163, 7, 33, 246, 161, 160, 159, 158, 157, 173],
    'right_eye':            [362, 398, 385, 386, 387, 388, 466, 263, 249, 390, 373, 374, 380, 381, 382],
    'left_iris':            [468, 469, 470, 471, 472],
    'right_iris':           [473, 474, 475, 476, 477],
    'left_eyebrow':         [55, 65, 52, 53, 46, 107, 66, 105, 63, 70],
    'right_eyebrow':        [285, 295, 282, 283, 276, 336, 296, 334, 293, 300]
}
_FACE_CONFIG_SELECTION = {key: value for key, value in _SELECTED_FACE_VERTICES.items() if key in CONFIG.SELECT_FACE_PARTS}


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
    if out_vid is not None:
        out_vid.release()
    return results


def serialize_solution_output(frames):
    def reduce(value):
        if value is None or not CONFIG.REDUCE_POSE_PRECISION:
            return value
        return round(value, CONFIG.REDUCE_POSE_PRECISION)

    def serialize_landmarks(landmarks):
        if landmarks is None:
            return None
        return [
            {
                "x": reduce(landmark.x),
                "y": reduce(landmark.y),
                "z": reduce(getattr(landmark, 'z', None)),
                "v": reduce(getattr(landmark, 'visibility', None))
            }
            for landmark in landmarks.landmark
        ]

    def select_face_sections(face_data):
        if not CONFIG.REDUCE_FACE_MESH:
            return face_data

        new_data = {}
        for key, index in _FACE_CONFIG_SELECTION.items():
            if key in ['left_iris', 'right_iris']:
                if not _HOLISTIC_ARGS['refine_face_landmarks']:
                    continue
                if key == 'left_iris' and 468 > len(face_data):
                    #LOG.warning('Left iris was not found in face data')
                    continue
                if key == 'right_iris' and 473 > len(face_data):
                    #LOG.warning('Right iris was not found in face data')
                    continue
            new_data[key] = [face_data[i] for i in index if i < len(face_data)]
        return new_data

    def serialize_frame(frame):
        return {
            "face_landmarks": select_face_sections(serialize_landmarks(frame.face_landmarks)),
            "pose_landmarks": serialize_landmarks(frame.pose_landmarks),
            "pose_world_landmarks": serialize_landmarks(frame.pose_world_landmarks),
            "left_hand_landmarks": serialize_landmarks(frame.left_hand_landmarks),
            "right_hand_landmarks": serialize_landmarks(frame.right_hand_landmarks)
        }

    return [serialize_frame(frame) for frame in frames]


def estimate_poses():
    dactyl = pd.read_csv(REPATH.ANNOTATION_DIR / 'dactyl.csv', delimiter=';')

    out_video_path = None
    for path in dactyl['local_path']:
        in_path = REPATH.PROJECT_ROOT / path

        if CONFIG.VIDEO_ANNOTATION_ENABLED:
            out_video_path = REPATH.DACTYL_POSE_DIR / in_path.name
            if REPATH.exists(out_video_path) and not CONFIG.FORCE_VIDEO_ANNOTATION:
                LOG.info(f"Video already exists: {out_video_path}")
                out_video_path = None

        result = holistic_process(in_path, out_video_path)
        if result is None:
            continue

        if CONFIG.POSE_ANNOTATION_ENABLED:
            annotation_path = REPATH.DACTYL_POSE_DIR / f'{in_path.stem}'
            pose_scribe.write(serialize_solution_output(result), annotation_path)


if __name__ == '__main__':
    estimate_poses()
