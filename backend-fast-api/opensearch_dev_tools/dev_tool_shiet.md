POST nivolaportalfaqs/_search
{
  "query": {
    "match_all": {}
  },
  "_source": ["question"],
  "size": 5000
}


POST nivolaportalfaqstext/_search
{
        "size": 11, "min_score": 0.50,
        "query": {
            "neural": {
                "embedding": {
                    "query_text": "come si crea una vm?",
                    "model_id": "rK6ChI4BuIvfyo_M-xDW",
                    "k": 11
                }
            }
        },
        "_source": ["id", "chunk", "link", "category", "title", "text"]
    }

POST nivolaportalfaqstext/_search
{
            "query": {
              "neural": {
                "embedding": {
                  "query_text": "come si crea una vm?",
                  "model_id": "rK6ChI4BuIvfyo_M-xDW",
                  "k": 5
                }
              }
            }
          }

PUT _cluster/settings
{
  "persistent": {
    "plugins": {
      "ml_commons": {
        "only_run_on_ml_node": "false",
        "model_access_control_enabled": "true",
        "native_memory_threshold": "99"
      }
    }
  }
}
# probably already executed

### 1. creare un nuovo gruppo di modelli
POST /_plugins/_ml/model_groups/_register
{
    "name": "streamlit_support_test",
    "description": "Group to test Embedding Models",
    "access_mode": "private"
}
# model_group_id = "wK5SEI8BuIvfyo_MxxBg"

# query all model groups
POST /_plugins/_ml/model_groups/_search
{
  "query": {
    "match_all": {}
  }
}

DELETE _plugins/_ml/model_groups/fvWMGo8Bm-5h-5tIVjgk

### 2. registrare i 3 modelli

#### search all
POST /_plugins/_ml/models/_search
{
  "query": {
    "match_all": {}
  },
  "size": 1000
}

#### delete 1
DELETE /_plugins/_ml/models/x66NEI8BuIvfyo_MZBAS


POST /_plugins/_ml/models/_register
{
  "name": "huggingface/sentence-transformers/multi-qa-MiniLM-L6-cos-v1",
  "version": "1.0.1",
  "model_group_id": "wK5SEI8BuIvfyo_MxxBg",
  "model_format": "TORCH_SCRIPT"
}
# model_id = aC-xGY8BShNSxJ2JnGWu

POST /_plugins/_ml/models/_register
{
  "name": "huggingface/sentence-transformers/msmarco-distilbert-base-tas-b",
  "version": "1.0.2",
  "model_group_id": "wK5SEI8BuIvfyo_MxxBg",
  "model_format": "TORCH_SCRIPT"
}
# model_id = 

POST /_plugins/_ml/models/_register
{
  "name": "huggingface/sentence-transformers/all-mpnet-base-v2",
  "version": "1.0.1",
  "model_group_id": "wK5SEI8BuIvfyo_MxxBg",
  "model_format": "TORCH_SCRIPT"
}
# task_id = 
GET /_plugins/_ml/tasks/-PVuGo8Bm-5h-5tIRzea
# model_id = 


### deployare i 3 modelli
#### POST /_plugins/_ml/models/$model_id/_deploy

POST /_plugins/_ml/models/aC-xGY8BShNSxJ2JnGWu/_deploy
POST /_plugins/_ml/models/xK6AEI8BuIvfyo_M5RBs/_deploy
POST /_plugins/_ml/models/xK6AEI8BuIvfyo_M5RBs/_deploy

### creare 3 pipiline
#### multi-qa: aC-xGY8BShNSxJ2JnGWu
#### msmarco-distilbert: xK6AEI8BuIvfyo_M5RBs
#### all-mpnet-base-v2: x66NEI8BuIvfyo_MZBAS

PUT /_ingest/pipeline/nivola_support_streamlit_multi_qa
{
  "description": "Streamlit support pipeline; Model: multi_qa ",
  "processors": [
    {
      "text_embedding": {
        "model_id": "aC-xGY8BShNSxJ2JnGWu",
        "field_map": {
          "text": "text_embedding"
        }
      }
    }
  ]
}

PUT /_ingest/pipeline/nivola_support_streamlit_msmarco_distilbert
{
  "description": "Streamlit support pipeline; Model: msmarco-distilbert",
  "processors": [
    {
      "text_embedding": {
        "model_id": "xK6AEI8BuIvfyo_M5RBs",
        "field_map": {
          "text": "text_embedding"
        }
      }
    }
  ]
}

PUT /_ingest/pipeline/nivola_support_streamlit_all-mpnet
{
  "description": "Streamlit support pipeline; Model: all-mpnet",
  "processors": [
    {
      "text_embedding": {
        "model_id": "x66NEI8BuIvfyo_MZBAS",
        "field_map": {
          "text": "text_embedding"
        }
      }
    }
  ]
}

### creare 3 indici

PUT /nivolaportalfaqs
{
  "settings": {
    "index.knn": true,
    "knn.algo_param.ef_search": 200,
    "default_pipeline": "faq_embedding_pipeline"
  },
  "mappings": { 
      "properties": {
          "question": {
            "type": "text"
          },
          "answer": {
            "type": "text"
          },
          "link": {
            "type": "text"
          },
          "embedding": {
              "type": "knn_vector", 
              "dimension": 0,
              "method": {
                  "name": "hnsw",
                  "space_type": "l2",
                  "engine": "nmslib",
                  "parameters": {
                      "ef_construction": 128,
                      "m": 24
                  }
              }
          }
      }
  }
}



### testare 3 indici con 100 ricerche semantiche e fare media degli score














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
#     or retrieve task_id, look up it and finally retrieve model_group_id
POST /_plugins/_ml/model_groups/_register
{
    "name": "streamlit_support_test",
    "description": "Group to test Embedding Models",
    "access_mode": "private"
}
# model_grou_id = tfVjGo8Bm-5h-5tIYjcH

# register model
#     retrieve model_id from the response
#     or retrieve task_id, look up it and finally retrieve model_id
POST /_plugins/_ml/models/_register
{
  "name": "amazon/neural-sparse/opensearch-neural-sparse-encoding-v1",
  "version": "1.0.1",
  "model_group_id": "tfVjGo8Bm-5h-5tIYjcH",
  "model_format": "TORCH_SCRIPT"
}

# task id u_W5Go8Bm-5h-5tI4ji6
GET /_plugins/_ml/tasks/i_X5Go8Bm-5h-5tIJTmL

# model_id = v_W5Go8Bm-5h-5tI5zid

# model_

POST /_plugins/_ml/models/_search
{
  "query": {
    "match_all": {}
  },
  "size": 1000
}


# deply model using model_id
POST /_plugins/_ml/models/B_XHGo8Bm-5h-5tI1Tm-/_deploy

# creare pipiline con 2 mapping

GET /_ingest/pipeline/
DELETE /_ingest/pipeline/test_2_embedding

PUT /_ingest/pipeline/test_2_embedding_mpnet
{
  "description": "test_2_embedding; Model: mpnet",
  "processors": [
    {
      "text_embedding": {
        "model_id": "B_XHGo8Bm-5h-5tI1Tm-",
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

PUT test_2_fields_mpnet
{
  "settings": {
    "index": {
      "knn": true,
      "default_pipeline": "test_2_embedding_mpnet",
      "knn.algo_param.ef_search": 844
    }
  },
  "mappings": {
    "properties": {
        "text_embedding": { 
          "type": "knn_vector",
          "dimension": 768,
          "method": {
            "name": "hnsw",
            "space_type": "l2",
            "engine": "nmslib",
            "parameters": {
                "ef_construction": 844,
                "m": 6
            }
          }
        },
        "category_embedding": { 
          "type": "knn_vector",
          "dimension": 768,
          "method": {
            "name": "hnsw",
            "space_type": "l2",
            "engine": "nmslib",
            "parameters": {
                "ef_construction": 844,
                "m": 6
            }
          }
        }
    }
  }
}


