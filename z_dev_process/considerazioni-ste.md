# Considerazioni 26 apr 2024
- ho testato vari modelli con vari metodi
- cosine similarity e linf funzionano meglio di l2
- cosine funziona molto bene se le domande sono in inglese (e dati in italiano)
- provare a trovare il read the docs in inglese o tradurre tutto in inglese
- per testare bene cosine simil

- in caso tradurre la domanda dell'utente in inglese e poi fare la neural search

mpnet con cosine sembra il migliore per ora, SEMBRA

# Considerazioni 29 apr 2024
- ho tradotto tutto il testo in inglese
- sto ristrutturando lo scraper di read the docs per migliorare i dati
- farò 3 ricerce che usano gli embedding
    tramite:
    - text_en
    - category_en
    - text

    prendo solo i documenti che sono in almeno 2/3 delle ricerche e li passo a claude

# Considerazioni 30 apr 2024
- gestire i dati nel prompt:
    - list[potenziali passaggi]
    - table[definizioni]
    - required_role
- passare dati aggiuntivi al prompt
    - definizioni di tecnologie
    - arricchimenti vari e necessari (if any)
- fare validazione del contesto con Mistral
    - magari anche altri passaggi possono essere fatti da Mistral
    - è molto meno costoso e comunque abbastanza potente per certe task
- capire se embeddare testi in inglese o italiano
    - se Inglese:
        - gestire bene input e output
        - la domanda se è in italiano tradurla in inglese con deepl(fare prompt per classificare lingua)
        - fare domanda a claude in inglese, con i dati del db in inglese
        - tradurre in italiano, valutare se usare deepl o claude
    - se Italiano:
        - in questo caso urge un embedding model ben funzionante con l'italiano
        - deve avere gli score alti nei casi appropriati
        - per ora non ne ho trovato nessuno, credo che dovrebbero essere proprio trainati in italiano
    - scelta ad oggi: dati in Inglese

# Considerazioni 3 maggio 2024
Ho creato il meccanismo per selezionare solo i documenti in comune ad almeno 2 delle 3 le ricerche, che sono effettuate tramite:
- text_en
- text (in italiano)
- category_en

Dai test fatti fino ad ora (non molti), trova i documenti giusti.
Funziona bene con le domande estese, ad esempio: 
- 'How can roles be assigned to a user?'
invece di 
- 'assign role'
E funziona ancora meglio se la domanda estesa è in Inglese.

Ora il mio focus andrà sull'implementazione di un sistema di Cache.

# Considerazioni 6 maggio 2024
Ho guardato [video del M.I.T](https://youtu.be/-pKNCjUhPjQ?t=2663) e ho capito come strutturare la cache.
Almeno credo.

# Considerazioni 7 maggio 2024
Ho rivisto il RAG Flow e aggiornato i TODO.
Oggi voglio sviluppare il sistema di cache

# Considerazioni 8 maggio 2024
Sto implementando il sistema di cache in parallelo al RAG in se per sè.
La modalità di ricerca 2 su 3 puo essere utile per permettere le ricerche in italiano, 
nel caso in cui non si puo tradurre la domanda.
Ho implementato parte della cache e session storage chat per tenere la cronologia dei messaggi.
Da riscrivere cache e session usando SQLite.

# Considerazioni 9 maggio 2024
Ho portato cache docs e lo storage delle conversazioni su SQLite,
li sto implementando nel codice principale.

