import spacy
from spacy.tokens import Doc, Token
from config.config import CONFIG


nlp = spacy.load(CONFIG.SPACY_MODEL_NAME)


class Word:
    """
    Represents a single word as a node of a tree.
    Since spacy Token is non-destructive and thus unchangeable,
    this class is specifically meant to be changeable for translation purposes.
    """
    def __init__(self, token, parent=None):
        if isinstance(token, Token):
            pass
        elif isinstance(token, str):
            doc = nlp(token)
            token = doc[0]
        else:
            raise TypeError(f"Unexpected type {type(token)}. Expected str or spacy.tokens.Token")

        # token
        self.token = token

        # changeable properties
        self.text = getattr(token, "text", '').lower()

        # tree properties
        self.parent = parent
        self.sentence = parent.sentence if self.parent else None
        self.children_left = []
        self.children_right = []
        self.is_left_child = False
        self.is_right_child = False

    def __repr__(self):
        return f"<Word: {self.text}>[{len(self.children_left)+len(self.children_right)}]"

    def __str__(self):
        return self.token.text


class Sentence:
    """
    Represents a single sentence as a tree of words.
    Since spacy Doc is non-destructive and thus unchangeable,
    this class is specifically meant to be changeable for translation purposes.
    """
    def __init__(self, text):
        if isinstance(text, str):
            self.doc = nlp(text)
        elif isinstance(text, Doc):
            self.doc = text
        else:
            raise TypeError(f"Unexpected type {type(text)}. Expected str or spacy.tokens.Doc.")

        self.root = None
        nodes = {token.i: Word(token) for token in self.doc}
        for token in self.doc:
            if token.head.i == token.i:  # The root node (a token that points to itself)
                self.root = nodes[token.i]
                self.root.sentence = self
            else:
                parent_node = nodes[token.head.i]
                child_node = nodes[token.i]
                child_node.parent = parent_node
                child_node.sentence = self
                if parent_node.token.i < child_node.token.i:
                    parent_node.children_right.append(child_node)
                    child_node.is_right_child = True
                else:
                    parent_node.children_left.append(child_node)
                    child_node.is_left_child = True

    def __repr__(self):
        return f"<Sentence from: {self.doc.text}>"

    def __str__(self):
        return self.string_tree(self.root).strip()

    def string_tree(self, node, level=0):
        string = ''
        for child in node.children_left:
            string += self.string_tree(child, level + 1)
        string += node.text + ' '
        for child in node.children_right:
            string += self.string_tree(child, level+1)
        return string
