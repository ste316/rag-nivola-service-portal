## Cache Coherence

- definizione: 
	dato un server centrale, come si può garantire che un sistema di Cache sia consistente in tutti i Client?

- regole:
	- you can't cache any data w/o lock
	- you must acquire lock to read from the server
	- to release the lock you must first write to the server 

- azioni:
	- request lock, client 2 server (c2s)
	- grant lock, server 2 client (s2c)
	- revoke lock, server 2 client (s2c)
	- release lock, client 2 server (c2s)

atomic multi-step operations
	- use transaction (db-like method)
	- lock (write) ALL resources you will delete, modify or create

- best practices:
	- distinguish from write and read locks
		- write is exclusive
		- read is shared
	- notify when a cache resources is/will be modified
		- E.G. Client-1 wants to modify a resource, all Clients with Read-Lock must be informed that the current cache they got is/will be outdated
		- Clients with Read-Lock can decide to wait or use the old cache

- crash handling
	- NOT HANDLED in this system
	- write ahead log (WAL)
		- write log before anything is done, a log for an immediate future action

https://www.geeksforgeeks.org/caching-system-design-concept-for-beginners/#2-how-does-cache-work
https://youtu.be/-pKNCjUhPjQ?t=2663

https://www.youtube.com/watch?v=r_ZE1XVT8Ao&ab_channel=NesoAcademy
https://www.youtube.com/watch?v=Ez1GK2imrsY&ab_channel=sudoCODE

## Description
The cache will
- contain 2 types:
	- RAG results 
	- OPENSEARCH results
- allow 3 actions
	- store
		- use chromadb ? (superlight and 0 latency)
		- data:
			- key:   user query
			- value: RAG and OPENSEARCH res
		- after returning the response to the user, store every res in both IT and EN
	- use
		- retrieve K similar question (with positive > negative voting from the user)
		- write a specific prompt
	- delete
		- when it's not used in the last 30 days
		- [FUTURE-FEATURES] when negative feedback sharply increase (TBD how)

Requirements:
- support RAG and OPENSEARCH
- use ChromaDB
- natively support IT and EN

## Cache Data Structure
- MAIN-INDEX [chromadb, lang=EN]
	contain:
	- doc
		- user_query (EN)
	- metadata:
		- final_response
			- en (full string)
			- it (full string)
		- docs_used (DOCS.id)
		- last_used (date)
	- example
		```python
		doc = "ciao, domanda del caso"
		metadata = {
			'final_response': {
				'en': 'value',
				'it': 'value'
			},
			'docs_used': [1, 2],
			"last_used": "dd/mm/yyyy"
		}
		```

- DOCS [json]
	contain:
	- key
		- id
	- value
		- full opensearch record
		- user_vote
			counters shared between all users
			- total 
				- number of times this cache record was used to produce a response
			- positive
			- negative
		- last_used (date)
	- example:
		```json
		{
			"doc_hash": {
				"data": {}, // full record copied from OpenSearch 
				"user_vote": {
					"total": 0,
					"positive": 0,
					"negative": 0
				},
				"last_used": "dd/mm/yyyy"
			}
		}
		```

- DELETE POLICY
	valid for both MAIN-INDEX and DOCS:
	- when it's not used in the last 30 days






