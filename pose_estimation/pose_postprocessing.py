import pickle
import pandas as pd

from util.path_resolver import PATH_RESOLVER as REPATH
from util.global_logger import GLOBAL_LOGGER as LOG
from pose_estimation.pose_scribe import pose_scribe

from warnings import simplefilter
simplefilter(action="ignore", category=pd.errors.PerformanceWarning)


xyz = ['x', 'y', 'z']

face_cols = list("""
    face_blendshapes._neutral
    face_blendshapes.browDownLeft
    face_blendshapes.browDownRight
    face_blendshapes.browInnerUp
    face_blendshapes.browOuterUpLeft
    face_blendshapes.browOuterUpRight
    face_blendshapes.cheekPuff
    face_blendshapes.cheekSquintLeft
    face_blendshapes.cheekSquintRight
    face_blendshapes.eyeBlinkLeft
    face_blendshapes.eyeBlinkRight
    face_blendshapes.eyeLookDownLeft
    face_blendshapes.eyeLookDownRight
    face_blendshapes.eyeLookInLeft
    face_blendshapes.eyeLookInRight
    face_blendshapes.eyeLookOutLeft
    face_blendshapes.eyeLookOutRight
    face_blendshapes.eyeLookUpLeft
    face_blendshapes.eyeLookUpRight
    face_blendshapes.eyeSquintLeft
    face_blendshapes.eyeSquintRight
    face_blendshapes.eyeWideLeft
    face_blendshapes.eyeWideRight
    face_blendshapes.jawForward
    face_blendshapes.jawLeft
    face_blendshapes.jawOpen
    face_blendshapes.jawRight
    face_blendshapes.mouthClose
    face_blendshapes.mouthDimpleLeft
    face_blendshapes.mouthDimpleRight
    face_blendshapes.mouthFrownLeft
    face_blendshapes.mouthFrownRight
    face_blendshapes.mouthFunnel
    face_blendshapes.mouthLeft
    face_blendshapes.mouthLowerDownLeft
    face_blendshapes.mouthLowerDownRight
    face_blendshapes.mouthPressLeft
    face_blendshapes.mouthPressRight
    face_blendshapes.mouthPucker
    face_blendshapes.mouthRight
    face_blendshapes.mouthRollLower
    face_blendshapes.mouthRollUpper
    face_blendshapes.mouthShrugLower
    face_blendshapes.mouthShrugUpper
    face_blendshapes.mouthSmileLeft
    face_blendshapes.mouthSmileRight
    face_blendshapes.mouthStretchLeft
    face_blendshapes.mouthStretchRight
    face_blendshapes.mouthUpperUpLeft
    face_blendshapes.mouthUpperUpRight
    face_blendshapes.noseSneerLeft
    face_blendshapes.noseSneerRight
""".split())
pose_cols = [f'pose_world_landmarks.{i}.{c}' for i in range(33) for c in xyz]
right_cols = [f'right_hand_world_landmarks.{i}.{c}' for i in range(21) for c in xyz]
left_cols = [f'left_hand_world_landmarks.{i}.{c}' for i in range(21) for c in xyz]

hand_cols = right_cols
hand_cols.extend(left_cols)
non_hand_cols = face_cols
non_hand_cols.extend(pose_cols)

valid_cols = []
valid_cols.extend(non_hand_cols)
valid_cols.extend(hand_cols)


def pose_parser(path):
    # load existing data
    raw_df = pose_scribe.read(path)
    if raw_df is None or raw_df.empty:
        return

    # if a valid column doesn't exist in raw data, create it and fill with blanks
    for col in valid_cols:
        if col not in raw_df.columns:
            raw_df[col] = -1

    # create valid df
    valid_df = raw_df[valid_cols].copy()

    # fill invalid values
    if valid_df[non_hand_cols].isna().any().any():
        valid_df.loc[:, non_hand_cols] = valid_df[non_hand_cols].interpolate(method='linear', limit_direction='both', axis=0)
    if valid_df[hand_cols].isna().any().any():
        valid_df.loc[:, hand_cols] = valid_df[hand_cols].fillna(-1)

    # trim the rows where both left and right hands are not in frame
    valid_df = valid_df[~valid_df[hand_cols].eq(-1).all(axis=1)]
    # trim 2 frames in and out if the clip is not too short
    if len(valid_df) >= 20:
        valid_df = valid_df[2:-2]

    return valid_df.astype(float).values.tolist()


def pose_postprocessing():
    annotation_d = pd.read_csv(REPATH.ANNOTATION_DIR / 'dactyl.csv', delimiter=';')
    annotation_w = pd.read_csv(REPATH.ANNOTATION_DIR / 'words_clean.csv', delimiter=';')
    annotation = pd.concat([annotation_d, annotation_w], axis=0, ignore_index=True)

    words = []
    poses = []
    lengths = []

    for word, path in zip(annotation['word'], annotation['annotation_csv_pkl']):
        LOG.info(f'Post-processing {path}')
        parsed = pose_parser(REPATH.PROJECT_ROOT / path)
        if parsed is not None and len(parsed) > 0:
            words.append(word)
            poses.append(parsed)
            lengths.append(len(parsed))
        else:
            LOG.warning(f'Parsing "{word}": {path} failed')

    full_data = {
        'word': words,
        'pose': poses,
        'length': lengths
    }

    output_file = REPATH.POSE_DATA_DIR / 'full_pose_dataset.pkl'
    LOG.info(f'Saving poses to {output_file}')
    with open(output_file, 'wb') as f:
        pickle.dump(full_data, f)


if __name__ == '__main__':
    pose_postprocessing()
