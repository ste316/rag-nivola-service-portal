
## update cluster settings
PUT _cluster/settings
{
  "persistent" : {
    "plugins.ml_commons.only_run_on_ml_node" : false,
    "plugins.ml_commons.model_access_control_enabled": "true",
    "plugins.ml_commons.allow_registering_model_via_url": "true",
    "plugins.ml_commons.native_memory_threshold": "99"

  }
}


## register custom model using hugging-face id
POST /_plugins/_ml/models/_register
{
  "name": "huggingface/sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
  "version": "1.0.1",
  "model_group_id": "tfVjGo8Bm-5h-5tIYjcH",
  "description": "embedding model that maps to 384 dymensions vector",
  "model_task_type": "TEXT_EMBEDDING",
  "model_config": {
    "embedding_dimension": 384,
    "model_type": "bert",
    "framework_type": "sentence_transformers"
  },
  "model_format": "TORCH_SCRIPT"
}

# read response and copy task_id
GET /_plugins/_ml/tasks/TASK_ID

model_id = TXhQKY8BlLTTsnWvljV0

# deploy model using model_id
POST /_plugins/_ml/models/TXhQKY8BlLTTsnWvljV0/_deploy

# creare pipiline con 2 mapping
PUT /_ingest/pipeline/test_paraphrase
{
  "description": "test_paraphrase; Model: paraphrase",
  "processors": [
    {
      "text_embedding": {
        "model_id": "TXhQKY8BlLTTsnWvljV0",
        "field_map": {
          "text": "text_embedding",
          "category": "category_embedding"
        }
      }
    }
  ]
}

### creare indice con 2 embedding fields
PUT test_paraphrase_cosine
{
  "settings": {
    "index": {
      "knn": true,
      "default_pipeline": "test_paraphrase",
      "knn.algo_param.ef_search": 420
    }
  },
  "mappings": {
    "properties": {
        "text_embedding": { 
          "type": "knn_vector",
          "dimension": 384,
          "method": {
            "name": "hnsw",
            "space_type": "cosinesimil",
            "engine": "nmslib",
            "parameters": {
                "ef_construction": 420,
                "m": 20
            }
          }
        },
        "category_embedding": { 
          "type": "knn_vector",
          "dimension": 384,
          "method": {
            "name": "hnsw",
            "space_type": "cosinesimil",
            "engine": "nmslib",
            "parameters": {
                "ef_construction": 420,
                "m": 20
            }
          }
        }
    }
  }
}




