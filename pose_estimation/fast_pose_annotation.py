import pandas as pd
from util.path_resolver import PATH_RESOLVER as REPATH
from util.global_logger import GLOBAL_LOGGER as LOG
from config.config import CONFIG


def fast_annotate():
    def annotation_pather(path, filetype='.txt'):
        path = path.replace('\\raw', '\\pose')
        path = path.replace('.mp4', filetype)
        if REPATH.exists(REPATH.PROJECT_ROOT / path):
            return path
        else:
            return None

    files = ['dactyl.csv', 'words.csv', 'words_clean.csv']
    for file in files:
        LOG.info(f'Annotating pose estimation files to {file}')
        annot_file = REPATH.ANNOTATION_DIR / file
        df = pd.read_csv(annot_file, delimiter=';')

        for file_type, save in CONFIG.POSE_ANNOTATION_FILE_TYPES.items():
            if not save:
                continue
            column_name = f'annotation{file_type.replace(".", "_")}'
            df[column_name] = df['local_path'].apply(annotation_pather, args=(file_type, ))

        df.to_csv(annot_file, index=False, sep=';')
        LOG.info(f'Saved {file}')


if __name__ == '__main__':
    fast_annotate()
