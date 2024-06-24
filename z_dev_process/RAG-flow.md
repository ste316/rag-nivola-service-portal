# New RAG Flow 
- utente sceglie quale lingua usare [IT | EN]
    - EN sarà tutto più accurato e veloce (dati in EN)
- utente: immette domanda
- traduzione domanda IT -> EN con deepl per semantic search in inglese
- 3 semantic search separate usando:
    - text_en
    - category_en
    - text (lang=IT)
    #### Come:
    - usare i documenti che sono in almeno 2/3 delle query
- Prompt:
    - gestire il prompt in modo intelligente
        aggiungere sezioni dinamicamente (list, table, required_role, additional infos)
    - usare tag XML per ogni entità separabile
    - assicurarsi che la domanda sia inerente ai giusti topic
        - a volte potrebbero esserci 0 documenti
        - all fine all good
        - controllare solo che la domanda sia in contesto
    - assicurarsi che Claude risponda in modo gentile, anche quando non ha una risposta
    - aggiungere tanti esempi di conversazioni
    - chiedere output nella lingua originale
- traduzione EN-IT per risposta con deepl in caso
- l'utente legge la risposta
- da un feedback [positivo | negativo | assente]

### CACHE
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

### NOTE:
1. performance:
    - ci sono molti passaggi che richiedono tempo (ad es. qualunque request)
    - usare i thread o async per runnare le 3 semantic search
    - concentrarsi su creare un sistema di caching per ogni possibile dato cachabile
        - make everything cachable
    - add some sleep(x) to have some improvement margin
2. conversation history
    - gestire storico messaggi nella chat
    - se sono troppi, fare una condensation e azzerare i messaggi mandati, non i messaggi visualizzati dall'utente
3. vedere RASA per gestire la conversazione o parte
    - vedere come salva i messaggi nel suo db
    - vedere altri meccanismi da estrapolare e riutilizzare

