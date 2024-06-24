# Nivola Service Portal Assistant WebApp

This repo contains a simple WebApp that gives access to a specialised [RAG](https://blogs.nvidia.com/blog/what-is-retrieval-augmented-generation/) about [Nivola ReadTheDocs](https://nivola-userguide.readthedocs.io/it/latest/).

## WebApp Details
1. Frontend
	- Streamlit ([frontend-streamlit-app](./frontend-streamlit-app/))
	- main-purpose: show RAG output in a fancy and appropriate way
	- communicate with the RAG through backend APIs

2. Backend
	- Fastapi ([backend-fast-api](./backend-fast-api/)):
	- main-purpose: define RAG structure and expose public APIs
	- communicate with OpenSearch, Bedrock and handles chat storage

## What's a RAG?
Watch [this quick and easy video](https://www.youtube.com/watch?v=T-D1OfcDW1M&ab_channel=IBMTechnology) to understand the general concept of RAG. \
If you aren't sure you grasped everything about, watch also [this video](https://www.youtube.com/watch?v=qppV3n3YlF8&ab_channel=IBMTechnology).

A RAG is an architecture built on top of [LLMs](https://en.wikipedia.org/wiki/Large_language_model) that leverages multiple Components to ensure LLM answers are coherent, up to date and correct.

Those alleged Components includes:
- Prompt
- Documents 
- VectorDB

Documents provide the Knowledge and Context, the VectorDB serves as effective Retrieval Method, finally the Prompt orchestrate the:
- LLM
- User Question
- Documents

The Prompt is the most critical Component, yet to accomplish the RAG's objective it needs each Components to work as intended.

## How is RAG implemented?
### Documents
Each documents repprensent an HTML section from [Nivola ReadTheDocs](https://nivola-userguide.readthedocs.io/it/latest/) site. \
The wiki-scraper is used to scrape and organize data. The key concept is defining a straightforward way to categorise documents. \
To categorise them you first need to divide the content semantically, in this implementation this step was already in place (HTML sections).

### VectorDB
[OpenSearch](https://opensearch.org/platform/search/vector-database.html) (opensource version of Elastic Search) is used as VectorDB. \
Every VectorDB needs an [Embedding Model](https://huggingface.co/blog/getting-started-with-embeddings) to classify texts and compute semantic distance between them.
OpenSearch related settings can be found [here](./backend-fast-api/opensearch_dev_tools/create_index_allmini.md). \
To summarize, it uses:
- [all-MiniLM-L12-v2](https://huggingface.co/sentence-transformers/all-MiniLM-L12-v2) as embedding model
- [cosine similarity](https://en.wikipedia.org/wiki/Cosine_similarity) as distance function
- 3 vector fields (text_en, text_it and category_en) to [semantically search](https://www.elastic.co/what-is/semantic-search) on

### Prompt
The prompt is focused on 3 topic:
- understand if the answer is in context
- understand if enough knowledge is available to produce an accurate answer
- produce the answer as complete and accurate as possible

The main strategy used to write the prompt is divide content into xml tags. \
The special tag: ***`<Inner Monologue (Claude)>`*** gives specific directives to ensure a proper answer management. \
Xml tags serves another purpose: give thinking spaces to Claude, this technique improve a lot the overall performance.

## Technical details
- ### Chat Data (file: db_chat.py)
	This file includes 3 DataClass and 1 Class to manage data

	DataClass serve the purpose of:
	- ensure data types and content consistency
	- define what actually is the entity itself
	- implement various method to handle the underlying data 

	#### The implemented DataClasses are:
	- Message
		- represent a Message in the Chat
		- underlying data: 
			- role; type: str; allowed value: 'user' or 'assistant'
			- content; type str; allowed value: any valid string
	- Docs
		- represent the Knowledge used by the LLM to generate an answer
		- underlying data: 
			- data; type: Dict
				- dict-key: document hash; type: str
				- dict-value: document content; type: dict
	- Conversation
		- represent the chat, therefore a list of Message
		- underlying data: List of Message object
		- check wether the Message alternate, one from user, one from assistant
		- should implement a Document
			- ##### DEV-NOTE: Doc dataclass should contains only 1 Document and this class should has a list of Doc objects
			- for development speed purposes it's not implemented
			- instead Docs class contains multiple Document
		- Document final-outcome:
			- Conversation dataclass do NOT check Documents as they are directly prompted into SQLite db

	#### The implemented Operational Class is conversation_db:
	- Interface layer between Python DataClasses and SQLite db
	- is the only class responsible for handling SQLite db
	- expose high level methods to manage everything related to Conversations 

- ### Retrieve Documents (file: opensearch.py)
	This file allow to:
	- upload documents to OpenSearch
	- perform semantic searches

	Both uploading and searching require the creation of an Index. \
	This [directory](./backend-fast-api/opensearch_dev_tools/) contains the procedures to setup Opensearch and create index suitable for semantic search. \
	The used index is defined in [create_index_allmini.md](./backend-fast-api/opensearch_dev_tools/create_index_allmini.md).

	Allmini Index is defined as follow:
	- Embedding Model: [all-MiniLM-L12-v2](https://huggingface.co/sentence-transformers/all-MiniLM-L12-v2)
	- Distance Function: [cosine similarity](https://en.wikipedia.org/wiki/Cosine_similarity)
	- Vector Fields:
		- text_en
		- text_it
		- category_en
	
	Vector Field is a special Index field that generates an index field to perform [semantic search](https://www.elastic.co/what-is/semantic-search) enabled by embedding. \
	For example text_en content is sent to the Embedding Model, which generates the embedding representation to store it in the relative embedding field: text_en_embedding. \
	As you can see in the Index creation process you map text_en to text_en_embedding, while also specifying the embedding method. \
	For further details, visit [OpenSearch Specification](https://opensearch.org/docs/latest/search-plugins/semantic-search/)

- ### Orchestrator (file: main.py)
	This file contain a Class to orchestrate the RAG, it is actually the most high level Layer.
	The are 3 very important function:
	- #### search_doc
		is responsible for searching the Documents. \
		Input:
		- K (integer)
			- define the top K most similar documents returned
		- User question (string)
			- utilized to search documents in 3 vector fields that return 3 results sets of lenght equals K parameter
		- only_3of3 (boolean)
			- define which documents are included in the function output
			- True
				- only the documents present in 3 out of 3 results sets are included
			- False
				- only the documents present in AT LEAST 2 out of 3 results sets are included
	- #### get_similar_docs
		- Is responsible for handling documents content.
		- The documents contains a lot of informations, only some are relevant for the LLM, this function selects it.
		- The selected ones are wraped properly in a string format to be passed to the LLM.
	- #### exec_rag
		- Is responsible for orchestrate chat handling, document retrieval and LLM input/output.
		- Therefore is the core function and the higest interface with the RAG.
	
	There are several functions in the Class, they serve the purpose of
	- data handling (major parts)
	- integration with public API
	- log some informations

## Run the RAG
Excluding OpenSearch instance, the RAG require to run 2 process:
- Frontend process
	- `cd frontend-streamlit-app`
	- `streamlit run main.py`
- Backend process
	- `cd backend-fast-api`
	- `fastapi run public_api.py`

## Possible Improvements?
1. ### User Question Analyzer
	Required to extrapolate the most useful words to find the documents that contain the wanted answer. \
	This component improve the VectorDB search capabilities, as you use only the right keywords to find related documents.

2. ### Documents re-Ranker
	In the current implementation, whenever a User asks something, all pre-retrieved documents are sent to the LLM.
	
	This component is required to:
	- avoid unnecessary costs (by not sending useless docs to the LLM)
	- ensure a precise answer

	A documents re-Ranker compare the User Question to each documents and select the most relevant docs from the already selected ones.

3. ### Overall Performance Analyzer
	This Component collects user satisfaction with the response given by the RAG. \
	It create a dataset with user satisfactions and RAG answers to analyze and explore what needs improvements.
