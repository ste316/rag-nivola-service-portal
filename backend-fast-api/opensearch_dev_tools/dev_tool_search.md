# classic search
POST test_2_fields_distilbert/_search
{
  "query": {
    "match_all": {}
  },
  "_source": {
      "exclude": [ "text_embedding", "category_embedding" ]
    },
  "size": 5000
}

# neural search
POST test_2_fields_mpnet/_search
{
  "min_score": 1,
  "_source": { "exclude": [ "text_embedding", "category_embedding" ] },
  "query": {
    "bool": {
      "should": [
        {
          "neural": {
            "category_embedding": {
              "query_text": "come posso creare un load balancer?",
              "model_id": "B_XHGo8Bm-5h-5tI1Tm-",
              "k": 33
              }
          }
        },
        {
          "neural": {
            "text_embedding": {
              "query_text": "come posso creare un load balancer?",
              "model_id": "B_XHGo8Bm-5h-5tI1Tm-",
              "k": 33
            }
        }
    }
  ]
  }
  }
}


POST test_2_fields/_search
{
  "min_score": 0.5,
  "_source": { "exclude": [ "text_embedding", "category_embedding" ] },
  "query": {
    "neural": {
      "category_embedding": {
        "query_text": "how can I create a virtual machine?",
        "model_id": "vfVjGo8Bm-5h-5tIyTej",
        "k": 33
      }
    }
  }
}

POST test_2_fields_mpnet/_search
{
  "min_score": 0.5,
  "_source": { "exclude": [ "text_embedding", "category_embedding" ] },
  "query": {
    "neural": {
      "category_embedding": {
        "query_text": "how can I create a virtual machine?",
        "model_id": "B_XHGo8Bm-5h-5tI1Tm-",
        "k": 33
      }
    }
  }
}

POST test_2_fields_distilbert/_search
{
  "min_score": 0.5,
  "_source": { "exclude": [ "text_embedding", "category_embedding" ] },
  "query": {
    "neural": {
      "text_embedding": {
        "query_text": "how can I create a virtual machine?",
        "model_id": "v_W5Go8Bm-5h-5tI5zid",
        "k": 33
      }
    }
  }
}

POST test_2_fields/_delete_by_query
{
  "query": {
    "match_all": {}
  }
}

