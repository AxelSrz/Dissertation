from elasticsearch import Elasticsearch
from numpy.random import choice
import pickle

def save_obj(obj, name ):
    with open(name + '.pkl', 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)

es = Elasticsearch()

docs_for_day = [3]*30
extra = choice(30,10)
for e in extra:
    docs_for_day[e] += 1

articles = []
editorial_count = {}
banned_editorials = []
ran_seed = choice(range(1,1000000))

for day, num_docs in enumerate(docs_for_day):
    weight_rank_1 = choice(range(1,4))
    weight_rank_2 = choice(range(1,4))
    weight_rank_3 = choice(range(1,4))
    docs_added = 0

    res = es.search(
        index="article_index",
        doc_type="article",
        body={
              "from" : int(0),
              "size" : int(100),
              "query": {
                "function_score": {
                  "query": {
                    "bool" : {
                          "must" : [
                            {
                              "term" : {
                                "published" : "2015-09-"+str(day+1).zfill(2)
                              }
                            },
                            {
                              "match_phrase": {
                                "detected-language": "en"
                              }
                            }
                          ],
                          "must_not": banned_editorials
                    }
                  },
                  "functions": [
                    {
                      "filter": {
                        "term": {
                          "moreover.editorial-rank": "1"
                        }
                      },
                      "weight": int(weight_rank_1)
                    },
                    {
                      "filter": {
                        "term": {
                          "moreover.editorial-rank": "2"
                        }
                      },
                      "weight": int(weight_rank_2)
                    },
                    {
                      "filter": {
                        "term": {
                          "moreover.editorial-rank": "3"
                        }
                      },
                      "weight": int(weight_rank_3)
                    },
                    {
                      "random_score": {
                        "seed": int(ran_seed)
                      }
                    }
                  ],
                  "score_mode": "sum"
                }
              }
            })
    for hit in res['hits']['hits']:
        editorial = hit['_source']['canonical-source-name']
        current_count = editorial_count.get(editorial, 0)
        if current_count < 2:
            articles.append(hit)
            editorial_count[editorial] = current_count + 1
            if editorial_count[editorial] == 2:
                banned_editorials.append({
                  "match" : {
                   "canonical-source-name" : editorial
                 }
                })
            docs_added +=1
            if docs_added == num_docs: break

    print('finished day: '+ str(day+1))
print('documents saved: '+str(len(articles)))
save_obj(articles, 'sample_articles_en')
print('Sample saved')
