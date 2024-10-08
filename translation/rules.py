from translation.tokens import Word


class UA2USLRulesHolder:
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

    def verb_infinitive(self, word):
        if not hasattr(word.token, 'pos_') or not hasattr(word.token, 'lemma_'):
            return
        if word.token.pos_ == 'VERB':
            word.text = word.token.lemma_
            morph = word.token.morph.to_dict()
            tense = morph['Tense']
            if self._auxiliary_verbs[tense] is not None:
                word.children_right.insert(0, self._auxiliary_verbs[tense])

    def negation_after_negated(self, word):
        if not word.children_left:
            return
        for part in self._negating_particle:
            for child in word.children_left:
                if part in child.text:
                    word.children_left.remove(child)
                    word.children_right.insert(0, Word('ні'))

    @staticmethod
    def adjectives_after_object(word):
        if not word.children_left:
            return
        for child in word.children_left:
            if child.token.pos_ == 'ADJ':
                word.children_left.remove(child)
                word.children_right.insert(0, child)

    def noun_plural_to_noun_noun(self, word):
        pass

