###################################################################################
# Test Multiple Embeded Fields Search

# modify cluster settings
PUT _cluster/settings
{
  "persistent" : {
    "plugins.ml_commons.only_run_on_ml_node" : false,
    "plugins.ml_commons.model_access_control_enabled": "true",
    "plugins.ml_commons.native_memory_threshold": "99"

  }
}

# create a model group 
#     retrieve model_group_id from the response
POST /_plugins/_ml/model_groups/_register
{
    "name": "streamlit_support_test",
    "description": "Group to test Embedding Models",
    "access_mode": "private"
}
# model_group_id = 

# register model
#     retrieve model_id from the response
#     or retrieve task_id, look up it and finally retrieve model_id
POST /_plugins/_ml/models/_register
{
  "name": "huggingface/sentence-transformers/multi-qa-MiniLM-L6-cos-v1",
  "version": "1.0.1",
  "model_group_id": "tfVjGo8Bm-5h-5tIYjcH",
  "model_format": "TORCH_SCRIPT"
}
# model_id = 8vVtGo8Bm-5h-5tIGDdD

# multi-qa model_id: 8vVtGo8Bm-5h-5tIGDdD

POST /_plugins/_ml/models/_search
{
  "query": {
    "match_all": {}
  },
  "size": 1000
}


# deply model using model_id
POST /_plugins/_ml/models/8vVtGo8Bm-5h-5tIGDdD/_deploy

# creare pipiline con 2 mapping

GET /_ingest/pipeline/
DELETE /_ingest/pipeline/test_2_embedding

PUT /_ingest/pipeline/test_2_embedding
{
  "description": "test_2_embedding; Model: multi_qa ",
  "processors": [
    {
      "text_embedding": {
        "model_id": "8vVtGo8Bm-5h-5tIGDdD",
        "field_map": {
          "text": "text_embedding",
          "category": "category_embedding"
        }
      }
    }
  ]
}

### creare indice con 2 embedding fields
DELETE test_2_fields

PUT test_2_fields
{
  "settings": {
    "index": {
      "knn": true,
      "default_pipeline": "test_2_embedding",
      "knn.algo_param.ef_search": 422
    }
  },
  "mappings": {
    "properties": {
        "text_embedding": { 
          "type": "knn_vector",
          "dimension": 384,
          "method": {
            "name": "hnsw",
            "space_type": "l2",
            "engine": "nmslib",
            "parameters": {
                "ef_construction": 422,
                "m": 6
            }
          }
        },
        "category_embedding": { 
          "type": "knn_vector",
          "dimension": 384,
          "method": {
            "name": "hnsw",
            "space_type": "l2",
            "engine": "nmslib",
            "parameters": {
                "ef_construction": 422,
                "m": 6
            }
          }
        }
    }
  }
}

# classic search
POST test_2_fields/_search
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
POST test_2_fields/_search
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
              "model_id": "8vVtGo8Bm-5h-5tIGDdD",
              "k": 33
              }
          }
        },
        {
          "neural": {
            "text_embedding": {
              "query_text": "come posso creare un load balancer?",
              "model_id": "8vVtGo8Bm-5h-5tIGDdD",
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
  "_source": { "exclude": [ "text_embedding", "category_embedding" ] },
  "query": {
    "neural": {
      "text_embedding": {
        "query_text": "come posso creare un load balancer?",
        "model_id": "8vVtGo8Bm-5h-5tIGDdD",
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
