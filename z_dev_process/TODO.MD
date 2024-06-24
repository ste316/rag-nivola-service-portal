# TODOs in order of priority and execution

- [docs] after the first message, retrieve also from docs in chat storage (use chroma)
    - pass to Claude only docs relative to the last question, not the entire conversation docs
- chat condensation
- [opensearch] analyze score to define minimum treshold for scores
    - mi interessa capire la correlazione tra similarity_score del documento 
    - e similarity score ricalcolato su cio che viene passato a Claude
- [frontend] enhance UX/UI
    - https://www.youtube.com/watch?v=sBhK-2K9bUc&ab_channel=CodingIsFun
    - add used links in the response
- make claude interact with opensearch to autonomously retrieve docs
- accuracy-1
- advanced cache
- [prompt-tester] code a simple prompt evaluator with Claude
- Increase accuracy-1
    - fare ricerca semantica su opensearch (gia implementata)
    - manipolazione dati varia (gia implementata)
    - fare semantic score tra i dati manipolati e la richiesta dell'utente (https://www.diariodiunanalista.it/posts/come-calcolare-la-similarita-tra-testi-di-un-sito-web-con-tf-idf-in-python/)
- [study] view: 
    - [new RAG techniques VIDEO](https://www.youtube.com/watch?v=sVcwVQRHIc8&ab_channel=freeCodeCamp.org) 
    - [a lot of resources and spunti utili](https://www.promptingguide.ai/research/rag) 
    - [GraphRAG](https://www.youtube.com/watch?v=r09tJfON6kE&ab_channel=AlexChao)
    - [evaluate prompt](https://www.youtube.com/watch?v=4rXfdzEVSsY&ab_channel=Streamlit)
    - [Retrieval Augmented Prompt R.A.P.](https://medium.com/@FastFedora/retrieval-augmented-prompting-enabling-prompt-switching-in-gpts-521821840afa)
- [backend-cache] define and develop caching system


# No Priority TODOs
- Increase accuracy-3
    - fare anche ricerche keyword based
    - aggiungerle nel sistema di aggragazione ricerce 
- Increase accuracy-4
    - aumentare la domanda [GAR-meets-RAG](https://arxiv.org/pdf/2310.20158)
- read some research:
    - [1](https://arxiv.org/pdf/2305.15294)
    - [2](https://arxiv.org/pdf/2312.10997)
    - [3 (normal article)](https://www.promptingguide.ai/research/rag)


# Action History
- [backend-opensearch] create a new index
    - creare un nuovo gruppo di modelli
    - deployare i 3
    - creare 3 pipiline
    - creare 3 indici
        - read this [article](https://opensearch.org/docs/2.0/search-plugins/knn/approximate-knn/#using-approximate-k-nn-with-filters)
    - testare 3 indici
    - dopo e solo dopo:
    - improve scraper
    - clean db.json
    - upload data to new index
- [scraper] adjust data handling
    - replace any <> to []
    - ensure category is translated correctly
- [backend-opensearch] reorg code
- [chat]     support conversation (classic conversation)
- [org]      move string gen to util
- [chat]     log questionn and score
- [search]   implement accuracy-2
    - handle opensearch scores
    - evalute them
    - order docs by importance based on scores
- [prompt-tester] code a simple prompt tester with Claude
- [prompt] craft 1 new Prompt
- [backend]  write hyper-simple fastapi endpoints (suitable to running on AWS Lambda)
- [frontend] write hyper-simple frontend using Streamlit
- [frontend] add support for multiple chats