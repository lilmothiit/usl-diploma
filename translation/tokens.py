import spacy
from spacy.tokens import Doc, Token
from translation.nlp import nlp


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
        elif isinstance(text, Doc) or isinstance(text, spacy.tokens.Span):
            self.doc = text
        else:
            raise TypeError(f"Unexpected type {type(text)}. Expected str, Doc or Span.")

        self.root = None
        self.root_at_end = False
        nodes = {token.i: Word(token) for token in self.doc}
        for token in self.doc:
            if token.head.i == token.i:  # The root node (a token that points to itself)
                self.root = nodes[token.i]
                self.root.sentence = self
            else:
                parent_node = nodes[token.head.i]
                child_node = nodes[token.i]

                if self._creates_cycle(child_node, parent_node):
                    continue

                child_node.parent = parent_node
                child_node.sentence = self
                if parent_node.token.i < child_node.token.i:
                    parent_node.children_right.append(child_node)
                    child_node.is_right_child = True
                else:
                    parent_node.children_left.append(child_node)
                    child_node.is_left_child = True

        self.tree_depth = self._calculate_depth(self.root)

    def __repr__(self):
        return f"<Sentence from: {self.doc.text}>"

    def __str__(self):
        return self.text(self.root).strip()

    def text(self, node=None, level=0):
        if node is None:
            node = self.root
        if level > self.tree_depth:
            return ' lol error'
        string = ''

        for child in node.children_left:
            string += self.text(child, level + 1)
        if not self.root_at_end or node is not self.root:
            string += node.text + ' '
        for child in node.children_right:
            string += self.text(child, level + 1)

        if node is self.root and self.root_at_end:
            string += self.root.text
        return string

    def text_tree(self, node=None, level=0):
        if node is None:
            node = self.root
        if level >= len(self.doc):
            return ' lol error'

        string = ''
        string += ' ' * 4 * level + node.text + '\n'
        for child in node.children_left:
            string += self.text_tree(child, level + 1)
        for child in node.children_right:
            string += self.text_tree(child, level + 1)
        return string

    def _creates_cycle(self, potential_ancestor, node):
        """
        Perform a depth-first search (DFS) to determine
        if potential_ancestor is an ancestor of node.
        """
        if node is None:
            return False
        if node == potential_ancestor:
            return True

        # Recursively check for cycles in both left and right children
        for child in node.children_left + node.children_right:
            if self._creates_cycle(potential_ancestor, child):
                return True

        return False

    def _calculate_depth(self, node):
        """
        Recursively calculate the depth of the tree from the given node.
        The depth of a node is 1 + the maximum depth of its children.
        """
        if not node.children_left and not node.children_right:
            return 1

        # Calculate depth for both left and right children
        left_depth = max((self._calculate_depth(child) for child in node.children_left), default=0)
        right_depth = max((self._calculate_depth(child) for child in node.children_right), default=0)

        return 1 + max(left_depth, right_depth)
