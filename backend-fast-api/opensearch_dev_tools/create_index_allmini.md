# 

# modify cluster settings
PUT _cluster/settings
{
  "persistent" : {
    "plugins.ml_commons.only_run_on_ml_node" : false,
    "plugins.ml_commons.model_access_control_enabled": "true",
    "plugins.ml_commons.native_memory_threshold": "99"

  }
}

# register model
#     retrieve model_id from the response
#     or retrieve task_id, look up it and finally retrieve model_id
POST /_plugins/_ml/models/_register
{
  "name": "huggingface/sentence-transformers/all-MiniLM-L12-v2",
  "version": "1.0.1",
  "model_group_id": $model_goup_id,
  "model_format": "TORCH_SCRIPT"
}
# read response and copy task_id
GET /_plugins/_ml/tasks/INSERT_task_id

# model_id = 

# deploy model using model_id
POST /_plugins/_ml/models/model_id/_deploy

# creare pipiline con 2 mapping
PUT /_ingest/pipeline/all_mini_3_fields
{
  "description": "all_mini_3_fields; Model: all-MiniLM-L12-v2",
  "processors": [
    {
      "text_embedding": {
        "model_id": "mXgYKo8BlLTTsnWvtjbF",
        "field_map": {
          "text_en": "text_en_embedding",
          "category_en": "category_en_embedding",
          "text": "text_it_embedding"
        }
      }
    }
  ]
}

### creare indice con 2 embedding fields
PUT test_all_mini_cosine
{
  "settings": {
    "index": {
      "knn": true,
      "default_pipeline": "all_mini_3_fields",
      "knn.algo_param.ef_search": 1000
    }
  },
  "mappings": {
    "properties": {
        "text_en_embedding": { 
          "type": "knn_vector",
          "dimension": 384,
          "method": {
            "name": "hnsw",
            "space_type": "cosinesimil",
            "engine": "nmslib",
            "parameters": {
                "ef_construction": 1000,
                "m": 40
            }
          }
        },
        "text_it_embedding": { 
          "type": "knn_vector",
          "dimension": 384,
          "method": {
            "name": "hnsw",
            "space_type": "cosinesimil",
            "engine": "nmslib",
            "parameters": {
                "ef_construction": 1000,
                "m": 40
            }
          }
        },
        "category_en_embedding": { 
          "type": "knn_vector",
          "dimension": 384,
          "method": {
            "name": "hnsw",
            "space_type": "cosinesimil",
            "engine": "nmslib",
            "parameters": {
                "ef_construction": 1000,
                "m": 40
            }
          }
        }
    }
  }
}

