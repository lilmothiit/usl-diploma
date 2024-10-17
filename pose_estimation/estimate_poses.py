import os
import cv2
import pandas as pd

import mediapipe as mp
from mediapipe.framework.formats import landmark_pb2
from mediapipe.tasks.python.vision import HolisticLandmarkerOptions, HolisticLandmarker
import mediapipe.python.solutions.drawing_utils as mp_drawing

from config.config import CONFIG
from util.global_logger import GLOBAL_LOGGER as LOG
from util.path_resolver import PATH_RESOLVER as REPATH

if __name__ == '__main__':
    from pose_scribe import pose_scribe
else:
    from pose_estimation.pose_scribe import pose_scribe

_HOLISTIC_OPTIONS = HolisticLandmarkerOptions(**CONFIG.POSE_ESTIMATION_OPTIONS)
_ANNOTATION_STYLES = CONFIG.VIDEO_ANNOTATION_STYLES


def draw_annotation(image, annotation):
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    for annot_type, *style in _ANNOTATION_STYLES:
        LOG.debug(f'Drawing annotation {annot_type}')
        annot = getattr(annotation, annot_type)
        if not annot:
            continue
        annot_proto = landmark_pb2.NormalizedLandmarkList()
        annot_proto.landmark.extend([
            landmark_pb2.NormalizedLandmark(x=landmark.x, y=landmark.y, z=landmark.z) for landmark in annot
        ])
        mp_drawing.draw_landmarks(image, annot_proto, *style)

    return image


def holistic_process(input_, output):
    _HOLISTIC = HolisticLandmarker.create_from_options(_HOLISTIC_OPTIONS)

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
    while in_vid.isOpened():
        success, image = in_vid.read()
        if not success:
            LOG.info("Reached end of video")
            break

        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=image)
        holistic_result = _HOLISTIC.detect_for_video(mp_image, int(in_vid.get(cv2.CAP_PROP_POS_MSEC)))
        results.append(holistic_result)

        if out_vid is not None:
            image = draw_annotation(image, results[-1])
            out_vid.write(image)

    in_vid.release()
    if out_vid is not None:
        out_vid.release()
    return results


def serialize_holistic_results(frames):
    def reduce(value):
        if value is None or not CONFIG.REDUCE_POSE_PRECISION:
            return value
        return round(value, CONFIG.REDUCE_POSE_PRECISION)

    def serialize_data(data):
        if not data:
            return None

        if hasattr(data[0], 'category_name') and hasattr(data[0], 'score'):
            return {datum.category_name : datum.score for datum in data}

        return {
            i: {
                "x": reduce(landmark.x),
                "y": reduce(landmark.y),
                "z": reduce(getattr(landmark, 'z', None)),
                "v": reduce(getattr(landmark, 'visibility', None)),
                "p": reduce(getattr(landmark, 'presence', None))
            }
            for i, landmark in enumerate(data)
        }

    def serialize_frame(frame):
        annot_dict = {}
        for annot_type, save in CONFIG.SELECTED_POSE_ANNOTATIONS.items():
            if not save:
                continue

            serialized_annot = serialize_data(getattr(frame, annot_type))
            if serialized_annot:
                annot_dict[annot_type] = serialized_annot

        return annot_dict

    return [serialize_frame(frame) for frame in frames]


def reevaluate_poses(df):
    selection_path = REPATH.ANNOTATION_DIR / 'words_selected.csv'
    if not REPATH.exists(selection_path):
        return df

    selection_df = pd.read_csv(selection_path, encoding='utf-8', delimiter=';')
    selected_df = df[df['word'].isin(selection_df['word'].to_list())]

    return selected_df


def estimate_poses():
    if not (CONFIG.POSE_ESTIMATION_SOURCE['dactyl'] or CONFIG.POSE_ESTIMATION_SOURCE['words']):
        LOG.error("No pose estimation sources were selected")
        return

    dactyl = pd.read_csv(REPATH.ANNOTATION_DIR / 'dactyl.csv', delimiter=';') \
        if CONFIG.POSE_ESTIMATION_SOURCE['dactyl'] else None
    words = pd.read_csv(REPATH.ANNOTATION_DIR / 'words_clean.csv', delimiter=';') \
        if CONFIG.POSE_ESTIMATION_SOURCE['words'] else None

    combined = []
    if dactyl is not None:
        combined.append((dactyl, REPATH.DACTYL_POSE_DIR))
    if words is not None:
        words = reevaluate_poses(words)
        combined.append((words, REPATH.WORD_POSE_DIR))

    out_video_path = None
    annotation_path = None
    for df, save_path in combined:
        for path in df['local_path']:
            in_path = REPATH.PROJECT_ROOT / path

            if CONFIG.VIDEO_ANNOTATION_ENABLED:
                out_video_path = save_path / in_path.name
                if REPATH.exists(out_video_path) and not CONFIG.FORCE_VIDEO_ANNOTATION:
                    LOG.info(f"Video already exists: {out_video_path}")
                    out_video_path = None

            annotation_path = save_path / f'{in_path.stem}'
            if not CONFIG.FORCE_POSE_ANNOTATION:
                if pose_scribe.all_selected_types_exist(annotation_path):
                    annotation_path = None

            if out_video_path is None and annotation_path is None:
                continue

            result = holistic_process(in_path, out_video_path)
            if result is None:
                LOG.error(f"No valid annotation found for {in_path.name}")
                continue

            if CONFIG.POSE_ANNOTATION_ENABLED:
                pose_scribe.write(serialize_holistic_results(result), annotation_path)


if __name__ == '__main__':
    estimate_poses()
