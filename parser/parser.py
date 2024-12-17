import nltk
import sys
from nltk.tokenize import word_tokenize

TERMINALS = """
Adj -> "country" | "dreadful" | "enigmatical" | "little" | "moist" | "red"
Adv -> "down" | "here" | "never"
Conj -> "and" | "until"
Det -> "a" | "an" | "his" | "my" | "the"
N -> "armchair" | "companion" | "day" | "door" | "hand" | "he" | "himself"
N -> "holmes" | "home" | "i" | "mess" | "paint" | "palm" | "pipe" | "she"
N -> "smile" | "thursday" | "walk" | "we" | "word"
P -> "at" | "before" | "in" | "of" | "on" | "to"
V -> "arrived" | "came" | "chuckled" | "had" | "lit" | "said" | "sat"
V -> "smiled" | "tell" | "were"
"""

NONTERMINALS = """
S -> NP VP
NP -> N
NP -> Adj NP
NP -> Det NP | P NP | P Det NP
NP -> NP Conj NP | NP Conj VP | NP Conj S
VP -> V
VP -> Adv VP | VP Adv
VP -> VP NP
VP -> VP Conj NP | VP Conj VP | NP Conj S
"""

grammar = nltk.CFG.fromstring(NONTERMINALS + TERMINALS)
parser = nltk.ChartParser(grammar)


def main():

    # If filename specified, read sentence from file
    if len(sys.argv) == 2:
        with open(sys.argv[1]) as f:
            s = f.read()

    # Otherwise, get sentence as input
    else:
        s = input("Sentence: ")

    # Convert input into list of words
    s = preprocess(s)

    # Attempt to parse sentence
    try:
        trees = list(parser.parse(s))
    except ValueError as e:
        print(e)
        return
    if not trees:
        print("Could not parse sentence.")
        return

    # Print each tree with noun phrase chunks
    for tree in trees:
        tree.pretty_print()

        print("Noun Phrase Chunks")
        for np in np_chunk(tree):
            print(" ".join(np.flatten()))


def preprocess(sentence):
    """
    Convert `sentence` to a list of its words.
    Pre-process sentence by converting all characters to lowercase
    and removing any word that does not contain at least one alphabetic
    character.
    """
    tokenized_sentence = word_tokenize(sentence)  # List of tokens in the sentence
    res = []
    print(tokenized_sentence)

    # Check every token
    for i in range(len(tokenized_sentence)):
        has_alphabetic_char = False
        # Check if there is at least ONE (1) alphanumeric character
        for char in tokenized_sentence[i]:
            if char.isalpha():
                has_alphabetic_char = True
        # Only keep the tokens with at least one alphnum char
        if has_alphabetic_char:
            res.append(tokenized_sentence[i].lower())

    return res


def np_chunk(tree):
    """
    Return a list of all noun phrase chunks in the sentence tree.
    A noun phrase chunk is defined as any subtree of the sentence
    whose label is "NP" that does not itself contain any other
    noun phrases as subtrees.
    """
    res = []
    # Check all subtrees in the sentence
    for t in tree.subtrees(filter=lambda x: x.label() == 'NP'):
        np_in_subtree = False
        # Check if there is a subtree with NP
        for st in t.subtrees(filter=lambda x: x.label() == 'NP'):
            # Found a subtree that isn't the original tree --> not NP chunk
            if st != t:
                np_in_subtree = True
        # If not, then the subtree is a noun phrase chunk
        if not np_in_subtree:
            res.append(t)
    
    return res


if __name__ == "__main__":
    main()
