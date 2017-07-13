var request = require('request');
var elasticsearch = require('elasticsearch');
var esClient = new elasticsearch.Client({
  host: '127.0.0.1:9200',
  requestTimeout: 120000,
  keepAlive: false,
  log: 'error'
});
var possible_search_types = ['Title','Content', 'Summary', 'Summary + Date', 'Bigram Search', 'Summary Entities', 'Semantic Content Search', 'Query Expansion']
var number_of_tweets = 10
var days_range = 3
var source_url = ""
var PythonShell = require('python-shell');

var py_options = {
  mode: 'json',
  scriptPath: 'C:/Users/raula/dissertation_demo/python_scripts',
  pythonOptions: ['-u'],
  args: []
};

exports.show = function(req, res){
  res.format({
    html: function(){
      res.render('search', {types: possible_search_types});
    },
    json: function(){
      res.json({});
    }
  });
};

exports.search = function (req, res) {
  var article_id = req.body.article_id
  var search_type = req.body.search_type
  //console.log(req.body);
  console.log(article_id);
  console.log(search_type);
  esClient.get({
    index: 'article_index',
    type: 'article',
    id: '"'+article_id+'"'
  }, function (error, response) {
    if(typeof response['_source'] != undefined){
      source_url = response['_source']['tracking-url']
    }
    switch (search_type) {
      case possible_search_types[0]:
        base_search(response['_source']['title'], res, req);
        break;
      case possible_search_types[1]:
        base_search(response['_source']['title']+" "+response['_source']['content'].split('\n').join(''), res, req);
        break;
      case possible_search_types[2]:
        base_search(response['_source']['title']+" "+response['_source']['summary'], res, req);
        break;
      case possible_search_types[3]:
        date_obj = new Date(response['_source']['published']);
        date_search(response['_source']['summary'], getFormattedDate(date_obj), res, req);
        break;
      case possible_search_types[4]:
        bigram_search(response['_source']['summary'], 'bigrams', res, req);
        break;
      case possible_search_types[5]:
        entity_search(response['_source']['stanford-entities'], 'summary', res, req)
        break;
      case possible_search_types[6]:
        bigram_search(response['_source']['content'],'semantic', res, req);
        break;
      case possible_search_types[7]:
        bigram_search(response['_source']['content'],'expansion', res, req);
        break;
    }
  });
}

exports.article_id = function(req, res) {
  var article_id = req.query.article_id
  esClient.get({
    index: 'article_index',
    type: 'article',
    id: '"'+article_id+'"'
  }, function (error, response) {
    base_search(response['_source']['title'], res, req);
  });
}

function asyncLoopInOrder(list, iterator, callback) {
  var nextItemIndex = 0;  //keep track of the index of the next item to be processed
  function report() {
    nextItemIndex++;
    // if nextItemIndex equals the number of items in list, then we're done
    if(nextItemIndex === list.length)
    callback();
    else
    // otherwise, call the iterator on the next item
    iterator(list[nextItemIndex], report);
  }
  // instead of starting all the iterations, we only start the 1st one
  iterator(list[0], report);
}

function daysQuery(base, range){
  str = "\"Sep "+base+"\""
  for(i=base+1; i<base+range; i++){
    str += " OR \"Sep "+i+"\""
  }
  return str
}

function getFormattedDate(date) {
  var year = date.getFullYear();

  var month = (1 + date.getMonth()).toString();
  month = month.length > 1 ? month : '0' + month;

  var day = date.getDate().toString();
  day = day.length > 1 ? day : '0' + day;

  return year+ '-' + month+ '-' + day;
}

function daysDict(base, range, text_query){
  qr = []
  for(i=base+1; i<base+range; i++){
    qr.push({"bool":{"must":[{"match_phrase":{"created_at":"Sep "+i}},text_query]}})
  }
  return qr
}

function match_array(element_list, field){
  qr = []
  element_list.forEach((item) => {
    d = {}
    d["match"] = {}
    d["match"][field] = item.replace("_", " ")
    qr.push(d);
  })
  return qr
}

function bigram_search(text_query, model_name, res, req){
  py_options.args.push(text_query)
  text_query = {'text_query':text_query}
  request.post({url:'http://localhost:5000/'+model_name, formData: text_query}, function (error, response, body) {
    if (error){
      console.log(error);
    }
    else {
      bigram_query(JSON.parse(body), res, req)
    }
  })
}

function entity_search(stanford_entities, entity_position, res, req){
  entities_list = []
  stanford_entities.forEach((item) => {
    if (item.position == entity_position) {
      entities_list.push(item.text)
    }
  })
  console.log(entities_list);
  esClient.search({
    index: 'tweet_index',
    type: 'tweet',
    size: number_of_tweets,
    body: {
      "query" : {
        "bool" : {
          "should" :match_array(entities_list, 'named_entities'),
          "filter":{
            "match_phrase":{
              "lang":"en"
            }
          }
        }
      }
    }
  }, function (error, response) {
    retrieve_tweets(response['hits']['hits'], res, req);
  });
}

function base_search(search_value, res, req){
  esClient.search({
    index: 'tweet_index',
    type: 'tweet',
    size: number_of_tweets,
    body: {
      "query": {
        "bool":{
          "must":{
            "match": {
              "text": search_value
            }
          },
          "filter":{
            "match_phrase":{
              "lang":"en"
            }
          }
        }
      }
    }
  }, function (error, response) {
    if(error){
      console.log("------------------------------------------------");
      console.log(error);
      console.log("------------------------------------------------");
    }
    retrieve_tweets(response['hits']['hits'], res, req);
  });
}

function date_search(search_value, date, res, req){
  esClient.search({
    index: 'tweet_index',
    type: 'tweet',
    size: number_of_tweets,
    body: {
      "query" : {
        "bool" : {
          "must" : {
            "match" : {
              "text" : search_value
            }
          },
          "filter" : {
            "bool": {
              "must": [
                {
                  "term" : {
                    "created_at" : date
                  }
                },{
                  "match_phrase":{
                    "lang":"en"
                  }
                }
              ]
            }
          }
        }
      }
    }
  }, function (error, response) {
    retrieve_tweets(response['hits']['hits'], res, req);
  });
}

function bigram_query(bigrams_list, res, req){
  console.log(bigrams_list);
  console.log(match_array(bigrams_list, 'text'));
  if(bigrams_list.length == 0){
    retrieve_tweets([{'_id':-1,'_score':-1}], res, req)
    return;
  }
  esClient.search({
    index: 'tweet_index',
    type: 'tweet',
    size: number_of_tweets,
    body: {
      "query" : {
        "bool" : {
          "should" :match_array(bigrams_list, 'text'),
          "filter":{
            "match_phrase":{
              "lang":"en"
            }
          }
        }
      }
    }
  }, function (error, response) {
    retrieve_tweets(response['hits']['hits'], res, req);
  });
}

function retrieve_tweets(es_tweet_array, res, req){
  console.log(req.get('accept'));
  if(req.get('accept') == 'application/json'){
    res.format({
      json: function(){
        res.json(es_tweet_array);
      }
    });
    return;
  }
  tweet_ids = [];
  es_tweet_array.forEach((item) => {
    tweet_ids.push(item['_id']);
  })
  var tweet_embeds = [];
  asyncLoopInOrder(tweet_ids, function (item, report) {
    request('http://publish.twitter.com/oembed?url=http%3A%2F%2Ftwitter.com%2FInterior%2Fstatus%2F'+item, function (error, response, body) {
      if (!error && response.statusCode == 200) {
        emb = JSON.parse(body)['html'];
        emb = emb.split("\n<script")[0];
        tweet_embeds.push(emb);
      }
      else if (error){
        console.log(error);
      }
      else {
        console.log("404 with id "+item);
      }
      report();
    })
  }, function() {
    res.format({
      html: function(){
        res.render('search', {types: possible_search_types, list_tweets: tweet_embeds, tracking_url: source_url});
      }
    });
  });
}
