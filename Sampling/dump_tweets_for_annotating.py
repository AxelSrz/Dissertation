import pickle
from elasticsearch import Elasticsearch
from random import shuffle

def load_obj(name ):
    with open(name + '.pkl', 'rb') as f:
        return pickle.load(f)

possible_search_types = ['Title','Content', 'Summary', 'Summary + Date', 'Bigram Search', 'Summary Entities', 'Semantic Content Search', 'Query Expansion']
articles = load_obj('sample_articles_en')
record_table = load_obj('sample_tweets_ranking_complete')

es = Elasticsearch()

last = 0
f = open('randomized_tweets_to_export_'+str(last)+'.txt','w', encoding='utf-8')
for index, article in enumerate(articles):
    article_id = article['_id'].replace('\"', '')
    added_tweets = set()
    article_tweets = []
    for search_type in possible_search_types:
        gen_tweets = (tweet for tweet in record_table[search_type] if tweet['article_id'] == article_id and tweet['tweet_id'] != -1)
        for tweet in gen_tweets:
            res = es.get(
                index="tweet_index",
                doc_type="tweet",
                id=tweet['tweet_id'])
            record_to_print = '\''+tweet['tweet_id']+'\''+'\t'+res['_source']['text'].replace('\n', '')
            if tweet['tweet_id'] not in added_tweets:
                article_tweets.append(record_to_print)
                added_tweets.add(tweet['tweet_id'])
    shuffle(article_tweets)
    if index // 10 > last:
        f.close()
        last = index // 10
        f = open('randomized_tweets_to_export_'+str(last)+'.txt','w', encoding='utf-8')
    f.write('With article id: '+article_id+' and link: '+article['_source']['original-url']+'\n')
    for t in article_tweets:
        f.write(t+'\n')
    f.write('----------'+'\n')

f.close()
