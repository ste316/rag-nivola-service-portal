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

# IF NOT EXIST create a model group 
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
  "name": "huggingface/sentence-transformers/all-mpnet-base-v2",
  "version": "1.0.1",
  "model_group_id": "INSERT",
  "model_format": "TORCH_SCRIPT"
}

# read response and copy task_id
GET /_plugins/_ml/tasks/INSERT_task_id

# model_id = 

# deploy model using model_id
POST /_plugins/_ml/models/model_id/_deploy

# creare pipiline con 2 mapping
PUT /_ingest/pipeline/test_2_embedding_mpnet
{
  "description": "test_2_embedding; Model: mpnet",
  "processors": [
    {
      "text_embedding": {
        "model_id": "INSERT_MODEL_ID",
        "field_map": {
          "text": "text_embedding",
          "category": "category_embedding"
        }
      }
    }
  ]
}

### creare indice con 2 embedding fields
PUT test_2_fields_mpnet_cosine
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
            "space_type": "linf",
            "engine": "nmslib",
            "parameters": {
                "ef_construction": 844,
                "m": 20
            }
          }
        },
        "category_embedding": { 
          "type": "knn_vector",
          "dimension": 768,
          "method": {
            "name": "hnsw",
            "space_type": "linf",
            "engine": "nmslib",
            "parameters": {
                "ef_construction": 844,
                "m": 20
            }
          }
        }
    }
  }
}

