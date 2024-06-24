# Procedure seguite per settare i prodotti AWS coinvolti nel RAG

## Opensearch
[Refs](https://medium.com/@zelal.gungordu/neural-search-on-opensearch-69d394495ab7)
0. Set OpenSearch Env

set cluster settings
```bash
PUT _cluster/settings
{
  "persistent" : {
    "plugins.ml_commons.only_run_on_ml_node" : false,
    "plugins.ml_commons.model_access_control_enabled": "true",
    "plugins.ml_commons.native_memory_threshold": "99"

  }
}
```

Search in the Opensearch docs how to:
- create a model groups
    - tip: use endpoint: /_plugins/_ml/model_groups
- create the model inside the model group 
    - tip: use endpoint: POST /_plugins/_ml/models/_register

1. Create Ingest Pipeline
- after /_ingest/pipeline/, insert the chosen name 
- add a description
- use the correct model_id, created in the previous step
- field_map
    - key is index field used as input
    - value is the new index field generated to store the embedding (output)
```bash
PUT /_ingest/pipeline/nivola_support_streamlit
{
  "description": "Streamlit support pipeline",
  "processors": [
    {
      "text_embedding": {
        "model_id": "rK6ChI4BuIvfyo_M-xDW",
        "field_map": {
          "text": "text_embedding"
        }
      }
    }
  ]
}
```

2. Choose an Embedding Model

db.json text field analysis:
- WORD count median value
    - 117.42
- CHAR count median value: 
    - 806.73

There's a lot of option, some of them are:
- [multi-qa-MiniLM-L6-cos-v1](https://huggingface.co/sentence-transformers/multi-qa-MiniLM-L6-cos-v1)
    - trained on question and answer
    - hard limit
        - 512 word
        - and trained on: 250 word texts
    - 384 dymensions
- [msmarco-distilbert-base-tas-b](https://huggingface.co/sentence-transformers/msmarco-distilbert-base-tas-b)
    - focused on semantic search
    - hard limit
        - not specified
    - 768 dymensions
- [all-mpnet-base-v2](https://huggingface.co/sentence-transformers/all-mpnet-base-v2)
    - focused on sematic search and clustering
    - hard limit
        -  384 word
    - 768 dymensions

- [all-MiniLM-L6-v2](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2)
    - already tested
    - return low scores
        - usually between 0.45 and 0.7 
        - in a scale from 0 to 1
    - 384 dymensions

https://opensearch.org/docs/latest/ingest-pipelines/processors/text-embedding/

```bash
POST /_plugins/_ml/models/_register
{
  # define which model you want to use
  # choose between the predefined from OpenSearch
  # or enable external Model and choose any model you want
  "name": "huggingface/sentence-transformers/msmarco-distilbert-base-tas-b",
  "version": "1.0.1",
  "model_group_id": "qq6BhI4BuIvfyo_MdBDE",
  "model_format": "TORCH_SCRIPT"
}
```

multi-qa: wq6AEI8BuIvfyo_M0xA_
msmarco-distilbert: xK6AEI8BuIvfyo_M5RBs
all-mpnet-base-v2: x66NEI8BuIvfyo_MZBAS


# kNN settings
Since out dataset is pretty small, I did the following consideration:
- exact k-NN
    - works well on small dataset, approximate k-NN is well suited for larger ones
- HNSW
    - it's a simple and effective solution to k-NN problem
    - effective as long as the index contains 10,000 or fewer datapoints (I guess records is the same? I guess)
    - do not scale with the index size, yet our index will be small
- nmslib 
    - idk
- distance function
    - l2
    - should fit I guess

[resource for point 1 and 2](https://opensearch.org/blog/Building-k-Nearest-Neighbor-(k-NN)-Similarity-Search-Engine-with-Elasticsearch/)

## create the index

```bash
PUT $index_name
{
  "settings": {
    "index": {
      "knn": true
    }
  },
  "mappings": {
    "properties": {
        "text": { # name of the field used as embedding
          "type": "knn_vector",
          "dimension": $DYM,
          "method": {
            "name": "hnsw",
            "space_type": "l2",
            "engine": "nmslib",
            "parameters": {
                # ef_search regulate based on vector size, max 10/20% more than len of vector
                # ef_construction regulate based on vector size, max 10/20% more than len of vector
                "ef_search": $X,
                "ef_construction": $X,
                "m": 6,
            }
          }
        },
        "category": { # name of the field used as embedding
          "type": "knn_vector",
          "dimension": $DYM,
          "method": {
            "name": "hnsw",
            "space_type": "l2",
            "engine": "nmslib",
            "parameters": {
                "ef_search": $X,
                "ef_construction": $X,
                "m": 6,
            }
          }
        },
    }
  }
}
```
sostitute with
PUT test_2_fields
{
  "settings": {
    "index": {
      "knn": true,
      "default_pipeline": "faq_embedding_pipeline",
      "ef_search": 422,
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


## search on multiple embedding fields

GET my-knn-index-1/_search
{
  "size": 2,
  "query": {
    "knn": {
      "my_vector_2": {
        "vector": [2, 3, 5, 6],
        "k": 2
      },
       "my_vector_1": {
        "vector": [2, 3, 5, 6],
        "k": 2
      },
    }
  }
}





