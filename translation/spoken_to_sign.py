from translation.tokens import Sentence

if __name__ == '__main__':
    test_texts = [
        'Я не довіряю людям.',
        'Я довіряла людям.',
        'Я довірятиму людям.',

        'Я маю коричневого собаку.',
        'Я маю гарного коричневого собаку.',

        'Я маю собаку давно.',
        'Сьогодні гарна погода.',
        'Я виходжу з дому.',

        'Ти маєш собаку? ',
        'Якого кольору халат лікаря?',
        'Як ти почуваєшся?',

        'Я купила.',
        'Смачний пиріг на тарілці.',
        'На тарілці мало пирогів.'
    ]

    test_ground_truth = [
        'Я довіряти людина людина.',
        'Я довіряти був людина людина.',
        'Я довіряти буду людина людина.',

        'Я мати собака коричневий.',
        'Я мати собака гарний коричневий.',

        'Я мати давно собака.',
        'Сьогодні погода добрий.',
        'Я виходити дім.',

        'Ти мати собака?',
        'Лікар халат колір який?',
        'Ти почувати себе як?',

        'Я купити вже',
        'Тарілка пиріг смачний',
        'Тарілка пиріг мало'
    ]

    for text in test_texts:
        sent = Sentence(text)
        print(sent)
