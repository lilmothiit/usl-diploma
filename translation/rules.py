from translation.tokens import Word
from config.config import CONFIG


class UA2USL:
    _auxiliary_verbs = {
        'Pres' : None,
        'Past' : Word('був'),
        'Fut' : Word('буде'),
    }
    _negating_particle = {
        'не',
        'ні',
        'ані'
    }

    def _verb_infinitive(self, word):
        if not hasattr(word.token, 'pos_') or not hasattr(word.token, 'lemma_'):
            return
        if word.token.pos_ == 'VERB':
            word.text = word.token.lemma_
            morph = word.token.morph.to_dict()
            tense = morph['Tense']
            if self._auxiliary_verbs[tense] is not None:
                word.children_right.insert(0, self._auxiliary_verbs[tense])

    def _negation_after_negated(self, word):
        if not word.children_left:
            return
        for part in self._negating_particle:
            for child in word.children_left:
                if part in child.text:
                    word.children_left.remove(child)
                    word.children_right.insert(0, Word('ні'))

    @staticmethod
    def _adjectives_after_object(word):
        if not word.children_left:
            return
        for child in word.children_left:
            if child.token.pos_ == 'ADJ':
                word.children_left.remove(child)
                word.children_right.insert(0, child)

    @staticmethod
    def _noun_plural_to_noun_noun(word):
        if word.token.pos_ == 'NOUN':
            morph = word.token.morph.to_dict()
            num = morph['Number']
            if num == 'Plur':
                word.text = word.token.lemma_
                word.children_left.append(Word(word.text))

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
                raise KeyError('Word isn\'t assigned as either left or right child')

    def translate(self, sentence):
        def _rule_order(word):
            if self._no_punctuation(word):
                return
            self._verb_infinitive(word)
            self._negation_after_negated(word)
            self._adjectives_after_object(word)
            self._noun_plural_to_noun_noun(word)

        def _translate_word(word):
            for child in word.children_left:
                _translate_word(child)
            _rule_order(word)
            for child in word.children_right:
                _translate_word(child)

        if sentence.root:
            _translate_word(sentence.root)


RULESETS = {
    'uk.ua' : UA2USL
}
RULESET = RULESETS[CONFIG.LANG_ALIAS]() if CONFIG.LANG_ALIAS in RULESETS else None
if not RULESET:
    raise ValueError(f'No ruleset defined for {CONFIG.LANG_ALIAS}')
