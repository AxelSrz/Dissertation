'''
Tokenisation
Various tokenisation methods
'''
import logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.ERROR)

import warnings
warnings.filterwarnings("ignore")

import re
import os
import sys

import spacy
import nltk
import json

from nltk import word_tokenize
from nltk.stem.porter import PorterStemmer
from nltk.corpus import stopwords

from gensim.models.phrases import Phraser

sent = sys.argv[1]


class Tokeniser(object):

    def __init__(self):
        self.porter = PorterStemmer()
        self.stop_words = stopwords.words("english")

    def tokenise(self, text, min_token_length=3):
        '''
        Tokenises a string of text by keeping only alphabetic characters.
        Returns a list of tokens.
        '''

        tokens = [self.porter.stem(w.lower()) for w in word_tokenize(text) if w not in self.stop_words]
        alphabet_regex = re.compile('[a-zA-Z]+')
        filtered_tokens = [t for t in tokens if alphabet_regex.match(t) and len(t) >= min_token_length]

        return filtered_tokens


class GencyTokeniser(object):

    def __init__(self):
        assert spacy.en.STOP_WORDS

        self.STOP_WORDS = spacy.en.STOP_WORDS
        nlp = spacy.load('en')
        nlp.pipeline = [nlp.tagger, nlp.parser]
        self.nlp = nlp
        self.bigram_model = Phraser.load('C:/Users/raula/dissertation_demo/python_scripts/bigram_model')

    def is_useful_token(self, token):
        # 90 = part_of_speech:NUM
        return token.is_alpha or (token.pos == 90)

    def apply_phrase_models(self, tokens):
        text = self.bigram_model[tokens]
        return [token for token in text if token not in self.STOP_WORDS]

    def tokenise(self, text):
        all_tokens = []
        for sentence in self.nlp(text, entity=False).sents:
            tokens = [token.lemma_ for token in sentence if self.is_useful_token(token)]
            all_tokens += self.apply_phrase_models(tokens)
        return all_tokens

    def bigrams(self, text):
        tokenized_text = self.tokenise(text)
        return [x for x in tokenized_text if "_" in x]

trained_tokenizer = GencyTokeniser()

print(json.dumps(trained_tokenizer.bigrams(sent)))
