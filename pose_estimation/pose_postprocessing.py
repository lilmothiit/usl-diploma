import gzip
import msgpack
import pandas as pd

from util.path_resolver import PATH_RESOLVER as REPATH
from util.global_logger import GLOBAL_LOGGER as LOG
from pose_estimation.pose_scribe import pose_scribe

from warnings import simplefilter
simplefilter(action="ignore", category=pd.errors.PerformanceWarning)


xyz = ['x', 'y', 'z']

face_cols = [f'face_landmarks.nose_tip.4.{c}' for c in xyz]
pose_cols = [f'pose_world_landmarks.{i}.{c}' for i in range(11, 17) for c in xyz]
right_cols = [f'right_hand_landmarks.{i}.{c}' for i in range(21) for c in xyz]
left_cols = [f'left_hand_landmarks.{i}.{c}' for i in range(21) for c in xyz]

hand_cols = right_cols
hand_cols.extend(left_cols)
non_hand_cols = face_cols
non_hand_cols.extend(pose_cols)

valid_cols = []
valid_cols.extend(non_hand_cols)
valid_cols.extend(hand_cols)


def pose_parser(path):
    # load existing data
    raw_df = pd.json_normalize(pose_scribe.read(path))

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

    return valid_df.astype(float).values.tolist()


def pose_postprocessing():
    annotation_d = pd.read_csv(REPATH.ANNOTATION_DIR / 'dactyl.csv', delimiter=';')
    annotation_w = pd.read_csv(REPATH.ANNOTATION_DIR / 'words_clean.csv', delimiter=';')
    annotation = pd.concat([annotation_d, annotation_w], axis=0, ignore_index=True)

    words = []
    poses = []
    lengths = []
    for word, path in zip(annotation['word'], annotation['annotation_path']):
        LOG.info(f'Post-processing {path}')
        parsed = pose_parser(REPATH.PROJECT_ROOT / path)
        if len(parsed) > 0:
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

    output_file = REPATH.WORD_POSE_DIR / '000000_full.msgpack.gz'
    LOG.info(f'Saving poses to {output_file}')
    with gzip.open(output_file, 'wb') as f:
        packed_data = msgpack.packb(full_data)
        f.write(packed_data)
        LOG.info(f'Saved file of size {len(packed_data)}')
        print()


if __name__ == '__main__':
    pose_postprocessing()
