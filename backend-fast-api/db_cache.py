from sqlite3 import connect
from costant import *
from pandas import DataFrame
from datetime import date, datetime
from lib_ import util

class cache_db:
    '''
    The cache will allow 3 actions
    - store
        - after returning the response to the user, store every res in both IT and EN
    - use
        - retrieve 3 similar question (with positive > negative voting from the user)
        - write a specific prompt
    - delete
        - every day start a cleaner
            - clean when it's not used in the last 30 days

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
            - data
                - retrieved_data string
                - link
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
    '''

    def __init__(self) -> None:
        if not util.create_operational_folder():
            raise Exception('Cache.__init__: cannot create operational folders')
        self.conn = connect(CACHE_DB_PATH, check_same_thread=False) # sqlite connect
        self.cursor = self.conn.cursor()

        self.cursor.execute(
            '''CREATE TABLE IF NOT EXISTS cache (
                    id TEXT PRIMARY KEY,
                    data TEXT,
                    link TEXT,
                    category TEXT,
                    last_used TEXT,
                    time_used INTEGER,
                    positive_vote INTEGER,
                    negative_vote INTEGER
                )'''
        )
        
    def retrieve_all(self, want_df: bool = False) -> DataFrame | dict:
        """
        Retrieve all cached records from the database.

        Args:
            want_df (bool, optional): Flag indicating whether to return the results as a DataFrame or a dictionary.
                If True, the results will be returned as a DataFrame. If False, the results will be returned as a dictionary.
                Defaults to False.

        Returns:
            DataFrame | dict: If want_df is True, returns a pandas DataFrame containing all cached records.
                If want_df is False, returns a dictionary where keys are document IDs and values are dictionaries containing
                document data, link, category, last used date, time used, positive vote, and negative vote.

        Notes:
            This function retrieves all cached records from the database and returns them either as a DataFrame or a dictionary.
            If want_df is True, the results are returned as a DataFrame. If want_df is False, the results are returned as a dictionary.

            The returned DataFrame or dictionary contains the following information for each cached record:
            - id: The unique identifier of the cached record.
            - data: The retrieved data string.
            - link: The link associated with the cached record.
            - category: The category of the cached record.
            - last_used: The date when the cached record was last used.
            - time_used: The number of times the cached record was used.
            - positive_vote: The number of positive votes received for the cached record.
            - negative_vote: The number of negative votes received for the cached record.
        """
        self.cursor.execute("SELECT * FROM cache")
        rows = self.cursor.fetchall()

        if want_df:
            # Creating the DataFrame
            df_data = []
            for row in rows:
                record = {
                    "id": row[0],
                    "data": row[1],
                    "link": row[2],
                    "category": row[3],
                    "last_used": row[4],
                    "time_used": row[5],
                    "positive_vote": row[6],
                    "negative_vote": row[7]
                }
                df_data.append(record)

            return DataFrame(df_data)
        else:
            # Creating the dictionary
            cache_dict = {}
            for row in rows:
                cache_dict[row[0]] = {
                    "data": row[1],
                    "link": row[2],
                    "category": row[3],
                    "last_used": row[4],
                    "time_used": row[5],
                    "positive_vote": row[6],
                    "negative_vote": row[7]
                }

            return cache_dict

    def add_new(self, new_data: dict) -> bool:
        """
        Add new documents to the cache and update existing ones.

        Args:
            new_data (dict): A dictionary containing new documents to be added to the cache.
                Keys are document IDs and values are dictionaries containing document data,
                link, category, etc.

        Returns:
            bool: True if the new documents are successfully added to the cache and existing ones
                are updated, False otherwise.

        Notes:
            This function updates the cache with new documents provided in the `new_data` dictionary.
            If a document with the same ID already exists in the cache, its time_used is incremented,
            and the last used date is updated to today's date. If a document is new, it is added to
            the cache with initial counters and date.

            The function returns True if the cache is successfully updated and saved, and False if there
            is an error during the process.
        """
        for doc_id, doc_data in new_data.items():
            self.cursor.execute(
                "INSERT OR REPLACE INTO cache (id, data, link, category, last_used, time_used, positive_vote, negative_vote) VALUES (?, ?, ?, ?, DATE('now'), COALESCE((SELECT time_used + 1 FROM cache WHERE id = ?), 1), ?, ?)",
                (doc_id, doc_data['data'], doc_data['link'], doc_data['category'], doc_id, doc_data['positive_vote'], doc_data['negative_vote'])
            )

        self.conn.commit()
        return True

    def clean_cache(self) -> bool:
        """
        Clean the cache by removing records older than CACHE_EXP_DAY value, specified in costant.py file.

        Returns:
            bool: True if the cache is successfully cleaned, False otherwise.

        Notes:
            This function loads a JSON file containing cached records, checks the last used date
            of each record, and removes records older than a specified threshold (CACHE_EXP_DAY).
            The cleaned records are then saved back to the JSON file.

            The function returns True if the cache is successfully cleaned and saved,
            and False if there is an error during the process.
        """
        today = date.today()
        self.cursor.execute("SELECT * FROM cache")
        rows = self.cursor.fetchall()

        for row in rows:
            last_used_date = datetime.strptime(row[4], '%d/%m/%Y')
            days_difference = (today - last_used_date.date()).days

            if days_difference >= CACHE_EXP_DAY:
                self.cursor.execute("DELETE FROM cache WHERE id = ?", (row[0],))
        
        self.conn.commit()
        return True
        
    def retrieve_cache_by_id(self, doc_ids: list[str]) -> dict:
        """
        Retrieve cached documents from the file based on the provided document IDs.

        Parameters:
            doc_ids (list[str]): A list of document IDs to retrieve.

        Returns:
            dict: A dictionary containing the cached documents found with their corresponding IDs as keys.
                The structure of the returned dictionary is as follows:
                {
                    "doc_id1": {
                        "data": str,
                        "link": str,
                        "category": str,
                        "last_used": str,
                        "time_used": int,
                        "positive_vote": int,
                        "negative_vote": int
                    },
                }

        Raises:
            Exception: If the provided doc_ids parameter is not a list of strings.
        """
        if not all(isinstance(doc_id, str) for doc_id in doc_ids):
            raise Exception('retrieve_cached_docs_by_id: doc_ids param must be a list of strings')

        self.cursor.execute("SELECT * FROM cache WHERE id IN ({seq})".format(seq=','.join(['?']*len(doc_ids))), doc_ids)
        rows = self.cursor.fetchall()

        cache_dict = {}
        for row in rows:
            cache_dict[row[0]] = {
                "data": row[1],
                "link": row[2],
                "category": row[3],
                "last_used": row[4],
                "time_used": row[5],
                "positive_vote": row[6],
                "negative_vote": row[7]
            }

        return cache_dict

def test():
    # Create an instance of the Cache class
    cache_instance = cache_db()

    # Example data to add to the cache
    new_data = {
        "doc_id1": {
            "data": "Example data 1",
            "link": "https://example.com/doc1",
            "category": "Category 1",
            "last_used": "01/01/2023",
            "time_used": 10,
            "positive_vote": 5,
            "negative_vote": 2
        },
        "doc_id2": {
            "data": "Example data 2",
            "link": "https://example.com/doc2",
            "category": "Category 2",
            "last_used": "02/01/2023",
            "time_used": 8,
            "positive_vote": 3,
            "negative_vote": 1
        }
    }

    # Add new documents to the cache
    cache_instance.add_new(new_data)

    # Retrieve cached documents by their IDs
    doc_ids = ["doc_id1", "doc_id2"]
    cached_docs = cache_instance.retrieve_cache_by_id(doc_ids)
    print("Cached documents:")
    print(cached_docs)

    # Load cache data as DataFrame
    cache_df = cache_instance.retrieve_all(want_df=True)
    print("Cache DataFrame:")
    print(cache_df)

    # Load cache data as dictionary
    cache_dict = cache_instance.retrieve_all()
    print("Cache dictionary:")
    print(cache_dict)

if __name__ == "__main__":
    test()

