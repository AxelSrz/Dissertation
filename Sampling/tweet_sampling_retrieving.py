import requests
import pickle
from datetime import datetime

def save_obj(obj, name ):
    with open(name + '.pkl', 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)

def load_obj(name ):
    with open(name + '.pkl', 'rb') as f:
        return pickle.load(f)

headers = {
        'Content-Type':'application/x-www-form-urlencoded',
        'Accept':'application/json'
       }
body = {
        'article_id':'',
        'search_type':''
       }


articles = load_obj('sample_articles_en')
possible_search_types = ['Title','Content', 'Summary', 'Summary + Date', 'Bigram Search', 'Summary Entities', 'Semantic Content Search', 'Query Expansion']
tweets_ranking = {}

i = 1
k = 1
for article in articles:
    article_date = datetime.strptime(article["_source"]["published"].split('T')[0],'%Y-%m-%d')
    body['article_id'] = article['_id'].replace("\"", '')
    i = 1
    for search_type in possible_search_types:
        if search_type not in tweets_ranking: tweets_ranking[search_type] = []
        body['search_type'] = search_type
        r = requests.post('http://localhost:3000/search',data=body, headers=headers, timeout=None)
        j = 1
        for tweet in r.json():
            record = {}
            record['article_id'] = body['article_id']
            record['tweet_id'] = tweet['_id']
            record['rank'] = j
            record['score'] = tweet['_score']
            tweets_ranking[search_type].append(record)
            i += 1
            j += 1
    print('Finished article: '+str(k)+' from day: '+str(article_date.day)+' with id: '+body['article_id'])
    k += 1

save_obj(tweets_ranking, 'sample_tweets_ranking_complete')
print('Sample saved')
