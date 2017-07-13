import pickle
from datetime import datetime

def load_obj(name ):
    with open(name + '.pkl', 'rb') as f:
        return pickle.load(f)

articles = load_obj('sample_articles_en')

for article in articles:
    print(article["_source"]["title"])
    #print(article['_id'].replace("\"", ''))
    #fecha = datetime.strptime(article["_source"]["published"].split('T')[0],'%Y-%m-%d')
    #print(fecha.day)
    print("---------------------------------------------")
