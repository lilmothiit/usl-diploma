import pandas as pd
from pymediainfo import MediaInfo
from util.global_logger import GLOBAL_LOGGER as LOG
from util.path_resolver import PATH_RESOLVER as REPATH


def _strip_id(text):
    text = text.split('.')[-2]
    text = text.split('\\')[-1]
    return int(text)


def _process_duplicates(data):
    def process_group(group):
        def get_unique(col):
            if group[col].nunique() == 1:
                return group[col].iloc[0]
            else:
                return set(group[col].unique())

        row = {'id': group['id'].iloc[0]}
        for column in data.columns:
            row[column] = get_unique(column)

        return row

    processed_data = data.groupby('id')[data.columns].apply(process_group)
    processed_df = pd.DataFrame(list(processed_data))

    return processed_df


def _get_video_metadata(video_path):
    try:
        media_info = MediaInfo.parse(video_path)
        for track in media_info.tracks:
            if track.track_type == "Video":
                return track.duration, track.width, track.height, track.frame_rate
    except Exception as e:
        LOG.exception(f"Failed to parse {video_path}: {e}")
        return None, None, None, None


def _extract_video_properties(data):
    # Define new columns for video properties
    data['duration'] = None
    data['width'] = None
    data['height'] = None
    data['frame_rate'] = None

    # Iterate over the rows in the DataFrame and extract properties for each video
    for index, row in data.iterrows():
        video_path = row['local_path']

        # Get video properties from metadata
        video_length, width, height, fps = _get_video_metadata(REPATH.PROJECT_ROOT / video_path)

        # Store the properties in the DataFrame
        data.at[index, 'duration'] = video_length
        data.at[index, 'width'] = width
        data.at[index, 'height'] = height
        data.at[index, 'frame_rate'] = fps

    return data


def clean_annotations():
    """
    Cleans up duplicate annotations.
    Collects all categories of one word into one list.
    Collects video metadata to new columns.
    Drops site link column.
    """
    LOG.info('Cleaning up annotations')
    annot_file = REPATH.ANNOTATION_DIR / 'words.csv'

    LOG.info(f'Loading annotation file at {annot_file}')
    df = pd.read_csv(annot_file, delimiter=';')

    LOG.info(f'Dropping site_path column')
    df.drop(columns=['site_path'], inplace=True)

    LOG.info(f'Extracting ID from file names')
    df['id'] = df['local_path'].apply(_strip_id)

    LOG.warning('Cleaning up ID duplicates. NOTE: Duplicate words may still exist in the dataset under different IDs')
    df = pd.DataFrame(_process_duplicates(df))
    LOG.info(f'Recording video metadata to new columns')
    df = _extract_video_properties(df)
    LOG.info(f'Dropping rows that reference a broken or non-existent video')
    df.dropna(inplace=True)

    LOG.info(f'Saving clean annotation to csv')
    df.to_csv(REPATH.ANNOTATION_DIR / 'words_clean.csv', index=False, sep=';')


if __name__ == '__main__':
    clean_annotations()
