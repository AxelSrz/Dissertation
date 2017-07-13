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
from scipy import spatial

import pickle

from nltk import word_tokenize
from nltk.stem.porter import PorterStemmer
from nltk.corpus import stopwords

from gensim.models.phrases import Phraser

#sent = sys.argv[1]
sent = "Pro-immigrant protesters got out some of their aggression against Donald Trump on Wednesday, slapping, punching and even picking the nose of a giant effigy of the Republican presidential front-runner during a boisterous rally in Los Angeles. It was one of several protests planned across the region ahead of Wednesday night's GOP debate in Simi Valley."


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

with open('C:/Users/raula/dissertation_demo/python_scripts/word2vec-300-17M.pkl ','rb') as f:
     word2vec = pickle.load(f)
     token_sent = trained_tokenizer.tokenise(sent)
     token_sent = list(filter(lambda x: x in word2vec.vocab, token_sent))
     central_vector = sum([word2vec[token] for token in token_sent])/len(token_sent)
     similarities = [(1 - spatial.distance.cosine(word2vec[token],central_vector), token) for token in token_sent]
     top_10 = [x[1] for x in sorted(similarities, key=lambda tup: tup[0], reverse=True)[:10]]
     similar_top_10 = [word2vec.most_similar(positive=token, topn=1)[0][0] for token in top_10]
     print(top_10 + similar_top_10)
     #res = [x[0] for x in word2vec.most_similar(positive=token_sent, topn=10)]
     #print(json.dumps(res))
