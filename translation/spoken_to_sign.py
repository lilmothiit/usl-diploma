from translation.tokens import Sentence, nlp
from translation.rules import RULESET

from util.global_logger import GLOBAL_LOGGER as LOG
from util.path_resolver import PATH_RESOLVER as REPATH
from util.annotator import Annotator

import faulthandler
import itertools
import json


def line_reader(filepath, skip_n):
    with open(filepath, 'r', encoding='utf-8') as file:
        # Skip the first N lines using itertools.islice
        for line in itertools.islice(file, skip_n, None):
            yield line.strip()


def spoken_to_sign():
    annotator = Annotator(REPATH.LANG_DATASET_DIR / 'spoken_to_sign.csv', header=['UA', 'USL'], delimiter='\t')

    file_status = {}
    if REPATH.exists(REPATH.LANG_DATASET_DIR / 'file_status.json'):
        with open(REPATH.LANG_DATASET_DIR / 'file_status.json', 'r') as f:
            file_status = json.load(f)
    save_status = open(REPATH.LANG_DATASET_DIR / 'file_status.json', 'w+')

    for file_path in REPATH.LANG_DATASET_DIR.iterdir():
        if not file_path.is_file() or not file_path.suffix == '.txt':
            continue
        if file_path.name in file_status:
            if file_status[file_path.name]['complete']:
                continue
        else:
            file_status[file_path.name] = {'complete': False, 'read_lines': 0, 'saved_lines': 0}

        texts = line_reader(file_path, file_status[file_path.name]['read_lines'])

        for doc in nlp.pipe(texts, disable=['senter', 'ner']):
            file_status[file_path.name]['read_lines'] += 1
            save_status.seek(0)
            save_status.write(json.dumps(file_status, indent=4) + '\n')

            if not doc.text.strip():
                continue

            sent = Sentence(doc)
            RULESET.translate(sent)
            text = str(sent)

            if not text or len(text) <= 5:
                continue

            annotator.record(line=[doc.text.strip(), str(sent).strip()])
            file_status[file_path.name]['saved_lines'] += 1

            if file_status[file_path.name]['read_lines'] % 100_000 == 0:
                LOG.info(f'Processed {file_status[file_path.name]["read_lines"]} lines, '
                         f'Saved {file_status[file_path.name]["saved_lines"]}')


def demo():
    test_texts = [
        'Я не довіряю людям.',
        'Я довіряла людям.',
        'Я довірятиму людям.',
        'Я купила.',
        'Я купуватиму.',
        'Я куплю.',

        'Я маю коричневого собаку.',
        'Я маю гарного коричневого собаку.',

        'Я маю собаку давно.',
        'Сьогодні гарна погода.',
        'Я виходжу з дому.',

        'Ти маєш собаку? ',
        'Якого кольору халат лікаря?',
        'Як ти почуваєшся?',

        'Смачний пиріг на тарілці.',
        'На тарілці мало пирогів.',
    ]

    test_ground_truth = [
        'я довіряти ні людина людина',
        'я довіряти був людина людина',
        'я довіряти буде людина людина',
        'я купити вже',
        'я купувати буде',
        'я купити потім',

        'я мати собака коричневий',
        'я мати собака гарний коричневий',

        'я мати собака давно',
        'сьогодні погода добрий',
        'я виходити дім',

        'ти мати собака',
        'лікар халат колір який',
        'ти почувати себе як',

        'тарілка пиріг смачний',
        'тарілка пиріг мало',
    ]

    print('ORIGINAL'.ljust(40), end='')
    print('TRANSLATED'.ljust(40), end='')
    print('TARGET')
    for text, gt in zip(test_texts, test_ground_truth):
        sent = Sentence(text)
        RULESET.translate(sent)
        print(text.ljust(40), end='')
        print(str(sent).ljust(40), end='')
        print(gt)


if __name__ == '__main__':
    faulthandler.enable()
    spoken_to_sign()
