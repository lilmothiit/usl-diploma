from translation.tokens import Word
from config.config import CONFIG
from util.global_logger import GLOBAL_LOGGER as LOG


class Lemmatizer:
    @staticmethod
    def translate(self, sentence):
        def _translate_word(word):
            children_left_copy = word.children_left[:]
            children_right_copy = word.children_right[:]
            for child in children_left_copy:
                _translate_word(child)
            word.text = word.token.lemma_.lower()
            for child in children_right_copy:
                _translate_word(child)

        if sentence.root:
            _translate_word(sentence.root)


class UA2USL:
    _auxiliary_verbs = {
        ('Past', 'Imp')  : Word('був'),
        ('Past', 'Perf') : Word('вже'),
        ('Fut', 'Imp')   : Word('буде'),
        ('Fut', 'Perf')  : Word('потім'),
    }

    @staticmethod
    def _no_punctuation(word):
        if word.token.is_punct:
            if word.is_left_child:
                word.parent.children_left.remove(word)
                return True
            elif word.is_right_child:
                word.parent.children_right.remove(word)
                return True
            else:
                #LOG.error(f'Word {str(word)} isn\'t assigned as a child. Can\'t remove root.')
                #LOG.warning('Punctuation mark was assigned as root. Is the sentence empty?')
                word.text = ''

    @staticmethod
    def _remove_parts_of_speech(word):
        if word.token.pos_ in ['ADP', 'CCONJ', 'SCONJ', 'SYM', 'X']:
            if word.is_left_child:
                word.parent.children_left.remove(word)
                return True
            elif word.is_right_child:
                word.parent.children_right.remove(word)
                return True
            else:
                #LOG.warning(f'Word {str(word)} isn\'t assigned as a child. Can\'t remove root.')
                word.text = ''

    def _verb_infinitive(self, word):
        if not hasattr(word.token, 'pos_') or not hasattr(word.token, 'lemma_'):
            return
        if word.token.pos_ == 'VERB':
            morph = word.token.morph.to_dict()
            if 'Tense' in morph.keys() and 'Aspect' in morph.keys():
                tense = morph['Tense']
                aspect = morph['Aspect']
                if (tense, aspect) in self._auxiliary_verbs:
                    word.children_right.insert(0, self._auxiliary_verbs[(tense, aspect)])

    @staticmethod
    def _lemmatize(word):
        if not hasattr(word.token, 'pos_') or not hasattr(word.token, 'lemma_'):
            return
        word.text = word.token.lemma_
        if '.' in word.text and not word.token.is_punct:
            word.text = Word(word.token.norm_).token.lemma_

    @staticmethod
    def _noun_plural_to_noun_noun(word):
        if word.token.pos_ == 'NOUN':
            morph = word.token.morph.to_dict()
            if 'Number' in morph.keys():
                num = morph['Number']
                if num == 'Plur':
                    word.text = word.token.lemma_
                    child = Word(word.text, parent=word)
                    child.is_left_child = True
                    word.children_left.append(child)

    @staticmethod
    def _negation_after_negated(word):
        if not word.children_left:
            return
        for part in ['не', 'ні', 'ані']:
            for child in word.children_left[:]:
                if part == child.text.lower():
                    word.children_left.remove(child)
                    word.children_right.insert(0, Word('ні'))
                    child.is_left_child = False
                    child.is_right_child = True

    @staticmethod
    def _subject_verb_object(word):
        for child in word.children_left[:]:
            if child.token.dep_ == 'dobj':
                word.children_left.remove(child)
                word.children_right.insert(0, child)
                child.is_left_child = False
                child.is_right_child = True
        for child in word.children_right[:]:
            if child.token.dep_ == 'nsubj':
                word.children_right.remove(child)
                word.children_left.insert(0, child)
                child.is_left_child = True
                child.is_right_child = False

    @staticmethod
    def _adjectives_after_object(word):
        if not word.children_left:
            return
        for child in word.children_left[:]:
            if child.token.pos_ == 'ADJ' or child.token.dep_ == 'amod':
                word.children_left.remove(child)
                word.children_right.insert(0, child)
                child.is_left_child = False
                child.is_right_child = True

    @staticmethod
    def _question_at_sentence_end(word):
        morph = word.token.morph.to_dict()
        if 'PronType' not in morph:
            return
        pron_type = morph['PronType']
        if pron_type in ['Int']:
            if word is word.sentence.root:
                word.sentence.root_at_end = True
            else:
                if word.is_left_child:
                    word.parent.children_left.remove(word)
                if word.is_right_child:
                    word.parent.children_right.remove(word)
                word.sentence.root.children_right.append(Word(word.text, parent=word.sentence.root))

    def translate(self, sentence):
        def _rule_order(word):
            # word removal
            if self._no_punctuation(word):
                return
            if self._remove_parts_of_speech(word):
                return
            # word form
            self._lemmatize(word)
            self._verb_infinitive(word)
            self._noun_plural_to_noun_noun(word)
            # sentence structure
            if word is word.sentence.root:
                self._subject_verb_object(word)
            self._adjectives_after_object(word)
            self._negation_after_negated(word)
            self._question_at_sentence_end(word)

        def _translate_word(word):
            children_left_copy = word.children_left[:]
            children_right_copy = word.children_right[:]
            for child in children_left_copy:
                _translate_word(child)
            _rule_order(word)
            for child in children_right_copy:
                _translate_word(child)

        if sentence.root:
            _translate_word(sentence.root)


RULESETS = {
    'uk.ua' : UA2USL
}
RULESET = RULESETS[CONFIG.LANG_ALIAS]() if CONFIG.LANG_ALIAS in RULESETS else Lemmatizer()
LEMMATIZER = Lemmatizer()
