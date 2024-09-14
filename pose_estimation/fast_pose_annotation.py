import pandas as pd
from util.path_resolver import PATH_RESOLVER as REPATH


def fast_annotate():
    def annotation_pather(path):
        path = path.replace('\\raw', '\\pose')
        path = path.replace('.mp4', '.msgpack.gz')
        if REPATH.exists(REPATH.PROJECT_ROOT / path):
            return path
        else:
            return None

    files = ['dactyl.csv', 'words.csv', 'words_clean.csv']
    for file in files:
        annot_file = REPATH.ANNOTATION_DIR / 'words.csv'
        df = pd.read_csv(annot_file, delimiter=';')
        df['annotation_path'] = df['local_path'].apply(annotation_pather)
        df.to_csv(annot_file, index=False, sep=';')


if __name__ == '__main__':
    fast_annotate()