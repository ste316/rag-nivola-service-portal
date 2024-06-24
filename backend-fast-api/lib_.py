from boto3 import setup_default_session, client, Session
from botocore.config import Config
from json import load, loads, dumps
from opensearchpy import OpenSearch
from langdetect import detect
from os import makedirs
from os.path import dirname
from costant import *
from secrets import choice
from string import ascii_letters, digits

class util:
    @staticmethod
    def load_json_file(file: str, encoding: str = 'utf-8') -> dict:
        '''
        Load JSON data from a file.

        Args:
            file (str): The path to the JSON file to be loaded.
            encoding (str): The encoding of the file (default is 'utf-8').

        Returns:
            dict: The loaded JSON data as a dictionary.

        Notes:
            This static method reads JSON data from the specified file path and returns it as a dictionary.
            It assumes that the file contains valid JSON data.
            If the file is not readable or an error occurs during reading, the method prints an error message and exits.
        '''
        with open(file, 'r', encoding=encoding) as f:
            if(f.readable()):
                return load(f)
            else: 
                print(f'Error while reading {file}')
                exit()
    
    @staticmethod
    def dump_json_file(file: str, data, encoding: str = 'utf-8') -> bool:
        '''
        Write data to a JSON file.

        Args:
            file (str): The path to the JSON file to be written.
            data: The data to be written to the file.
            encoding (str): The encoding of the file (default is 'utf-8').

        Returns:
            bool: True if the data is successfully written to the file, False otherwise.

        Notes:
            This static method writes the provided data to the specified JSON file.
            It assumes that the data can be serialized to JSON format.
            If the file cannot be written or an error occurs during writing, the method prints an error message and returns False.
            Otherwise, it returns True after successfully writing the data to the file.
        '''
        json_data = dumps(data, ensure_ascii=False, indent=4)
        makedirs(dirname(file), exist_ok=True)

        with open(file, 'w', encoding=encoding) as f:
            if(f.writable()):
                f.write(json_data)
                return True
            else: 
                print(f'Error while writing {file}')
                return False

    @staticmethod
    def create_operational_folder() -> bool:
        '''
        Create operational folders for cache and conversation databases.

        Returns:
            bool: True if the folders are successfully created or already exist, False otherwise.
        '''
        dirs = [CACHE_DB_PATH, CONVERSATION_DB_PATH]

        try:
            for d in dirs:
                makedirs(dirname(d), exist_ok=True)
        except:
            return False
        return True

    @staticmethod
    def load_settings() -> dict:
        '''
        Load settings from the 'settings.json' file.

        Returns:
            dict: A dictionary containing the loaded settings.
        '''
        return util.load_json_file('settings.json')
    
    @staticmethod
    def detect_language_langdetect(text: str) -> str:
        '''
        Detect the language of the given text using the Langdetect library.

        Args:
            text (str): The text whose language needs to be detected.

        Returns:
            str: The detected language code (e.g., 'en' for English).
        '''
        try:
            detected_language = detect(text)
            return detected_language
        except Exception as e:
            print("An error occurred:", e)
            return None

    @staticmethod
    def generate_random_string(length=64):
        """
        Generate a random string of specified length using the random module.

        Args:
        length (int): The length of the random string to generate. Default is 20.

        Returns:
        str: A random string of specified length.
        """

        characters = ascii_letters + digits
        return ''.join(choice(characters) for _ in range(length))

    @staticmethod
    def is_str_list(data) -> bool:
        '''
        Check if all elements in the given data list are of type str.

        Args:
            data (list): The list to be checked.

        Returns:
            bool: True if all elements in the list are of type str, False otherwise.
        '''
        return all(isinstance(item, str) for item in data) if isinstance(data, list) else False

    @staticmethod
    def is_dict_list(data) -> bool:
        '''
        Check if all elements in the given data list are of type dict.

        Args:
            data (list): The list to be checked.

        Returns:
            bool: True if all elements in the list are of type dict, False otherwise.
        '''
        return all(isinstance(item, dict) for item in data) if isinstance(data, list) else False

class aws:
    def __init__(self, load_bedrock: bool = False, load_opensearch: bool = False) -> None:
        self.settings = util.load_settings()
        if load_bedrock: self.bedrock = self.get_bedrock()
        if load_opensearch: self.opensearch = self.get_opensearch()
    
    def get_opensearch(self) -> OpenSearch:
        ''' 
        Get the OpenSearch client for interacting with an OpenSearch service.

        Returns:
            OpenSearch: An OpenSearch client instance.

        Notes:
            This function initializes and returns an OpenSearch client with the specified configuration 
            parameters, including the OpenSearch URL, username, and password. It is used for interacting 
            with an OpenSearch service.
        '''
        return OpenSearch(
            hosts=[self.settings['opensearch_url']],
            http_auth=(self.settings['username_opensearch'], self.settings['password_opensearch']),
            verify_certs=False
        )
    
    # for local test only
    def get_bedrock(self):
        ''' 
        Get the Bedrock client session.

        Returns:
            Session: The Bedrock client session for making requests.

        Notes:
            This function retrieves the Bedrock client session based on the configured bedrock_region
            and temporary session credentials obtained using AWS STS.
        '''
        region = self.settings['bedrock_region']
        session = setup_default_session(
            aws_access_key_id=self.settings['access_key'],
            aws_secret_access_key=self.settings['secret_key'],
            region_name=region
        )
        
        sts_client = client('sts')
        # Get a session token
        session_token = sts_client.get_session_token(
            DurationSeconds=3600
        )

        # Create a session with the temporary credentials
        session = Session(
            aws_access_key_id=session_token['Credentials']['AccessKeyId'],
            aws_secret_access_key=session_token['Credentials']['SecretAccessKey'],
            aws_session_token=session_token['Credentials']['SessionToken'],
            region_name=region
        )
        
        client_session = session.client('bedrock-runtime', config=Config(
            region_name=region,
            retries={
                'max_attempts': 5,
                'mode': 'standard'
            }
        ))
        return client_session

    def call_claude_3(self,
            system_prompt, messages: list[dict], bedrock_runtime = None, 
            model_id: str = 'anthropic.claude-3-sonnet-20240229-v1:0', 
            temperature: float = 0.0, max_tokens: int = 3000
        ) -> str:
        ''' 
        Call the Anthropic Claude-3 model for text generation.

        Args:
            system_prompt (str): The system prompt for text generation.
            messages (list[dict]): A list of messages containing role and content.
            bedrock_runtime: The Bedrock runtime object.
            model_id (str): The ID of the model to use. Defaults to 'anthropic.claude-3-opus-20240229-v1:0'.
            temperature (float): The temperature parameter for text generation. Defaults to 0.0.
            max_tokens (int): The maximum number of tokens to generate. Defaults to 3000.

        Returns:
            str: The generated text response.

        Notes:
            This function calls the Anthropic Claude-3 model for text generation using the provided system_prompt and messages.
            If bedrock_runtime is not provided, it is retrieved based on the configured bedrock_region.
            The function returns the generated text response.
        '''

        ''' example of messages structure
        "messages": [
            {
                "role": "",
                "content": [
                    { "type": "image", "source": { "type": "base64", "media_type": "image/jpeg", "data": "content image bytes" } },
                    { "type": "text", "text": "content text" }
                ]
            }, 
            {...}
        ],
        https://docs.aws.amazon.com/bedrock/latest/userguide/model-parameters-anthropic-claude-messages.html#api-inference-examples-claude-messages-code-examples
        '''
        # supported models: [in ascending order of power] modelId = 'anthropic.claude-3-haiku-20240307-v1:0' modelId = "anthropic.claude-3-sonnet-20240229-v1:0" modelId = 'anthropic.claude-3-opus-20240229-v1:0'
        if bedrock_runtime == None:
            bedrock_runtime = self.get_bedrock()

        body=dumps(
            {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": max_tokens,
                "system": system_prompt,
                "messages": messages,
                'temperature': temperature
            }
        )

        response = bedrock_runtime.invoke_model(body=body, modelId=model_id)
        response_body = loads(response.get('body').read())
        return response_body['content'][0]['text']

from chromadb import Collection, PersistentClient, ClientAPI
from lib_ import util

class chroma_wrapper:
    def __init__(self, persist_directory: str) -> None:
        self.client = self.create_or_load_db(persist_directory)

    def create_or_load_db(self, persist_directory: str) -> ClientAPI:
        return PersistentClient(path=persist_directory)

    def reset_db(self) -> bool:
        '''
        Resets the database. This will delete all collections and entries.

        Returns:
            bool: True if the database was reset successfully.
        '''
        return self.client.reset()

    def create_collection(self, name: str) -> Collection:
        """
        Create a new collection in the database with the specified name.

        Args:
            name (str): The name of the collection to create.

        Returns:
            Collection: The newly created collection object.

        Notes:
            This function creates a new collection in the database with the specified name.
            The collection is created with default metadata specifying the HNSW space as "cosine".
            The function returns the newly created Collection object.
        """
        print(f'chromadb: creating collection: {name}...')
        return self.client.get_or_create_collection(
            name=name,
            metadata={"hnsw:space": "cosine"} # l2 is the default
        )
    
    def get_collection(self, name: str, create_if_fail: bool = False) -> Collection:
        """
        Retrieve a collection from the database by its name.

        Args:
            name (str): The name of the collection to retrieve.
            create_if_fail (bool, optional): If True and the collection doesn't exist, create it.
                                            Defaults to False.

        Returns:
            Collection or None: The retrieved collection if it exists, None if it doesn't exist
                                and create_if_fail is False, or the newly created collection
                                if create_if_fail is True and the collection didn't exist before.

        Notes:
            This function attempts to retrieve a collection from the database with the specified name.
            If the collection exists, it returns the Collection object.
            If the collection doesn't exist and create_if_fail is False, it returns None.
            If the collection doesn't exist and create_if_fail is True, it attempts to create the collection
            using the `create_collection` method, and returns the newly created Collection object.
            Any ValueError raised during the retrieval process indicates that the collection doesn't exist,
            and it's handled accordingly based on the value of create_if_fail.
        """
        c = None
        try:
            c = self.client.get_collection(name=name)
        except ValueError:
            # ValueError if the collection doesn't exist
            if create_if_fail: 
                c = self.create_collection(name=name)
        except Exception:
            pass
        return c
    
    def delete_collection(self, name: str) -> bool:
        """
        Delete a collection from the database.

        Args:
            name (str): The name of the collection to delete.

        Returns:
            bool: True if the collection was successfully deleted or doesn't exist,
                False if an error occurred during the deletion process.
        """
        print(f'chromadb: deleting collection: {name}')
        try:
            self.client.delete_collection(name=name)
        except ValueError:
            # ValueError if the collection doesn't exist
            # therefore already deleted
            pass
        except Exception:
            return False

        return True
    
    def get_collection_len(self, name: str) -> int:
        """
        Get the number of documents in the specified collection.

        Args:
            name (str): The name of the collection to retrieve.

        Returns:
            int: The number of documents in the collection.

        Notes:
            This function retrieves the collection with the specified name from the database.
            If the collection does not exist, it returns 0.
            The function then returns the number of documents in the collection.
        """
        c = self.get_collection(name=name, create_if_fail=False)
        return c.count()
    
    def load_data(self, collection_name: str, data: list[dict]):
        """
        Add data to a Chroma collection.

        Args:
            collection_name (str): The name of the collection to which the data will be added.
            data (list[dict]): 
                A list of dictionaries containing the data to be added. Each dictionary should contain the following keys: 'document', 'metadata', and 'id'.
            The 'document' key should contain the raw document data (str). 
            The 'metadata' key should contain a dictionary of metadata associated with the document, 
            Finally the 'id' key should contain a unique identifier for the document. 

        Returns:
            bool: True if the data was successfully added to the collection, False otherwise.

        Raises:
            ValueError: If the provided data is not of type list[dict] or if any dictionary in the list does not contain the required keys.

        Examples:
            # Add data to a collection
            success = load_data(collection_name="my_collection", data=[
                {'document': 'Lorem ipsum...', 'metadata': {'chapter': '3', 'verse': '16'}, 'id': 'doc1'},
                ...
            ])
        """
        c = self.get_collection(name=collection_name, create_if_fail=True)
        # check if data is a list of dicts and contains the expected columns
        keys_exist = all({'document', 'metadata', 'id'}.issubset(d.keys()) for d in data) \
            and (isinstance(data, list) and all(isinstance(item, dict) for item in data))

        if keys_exist:
            documents = [d['documents'] for d in data]
            metadatas = [d['metadatas'] for d in data]
            ids = [d['ids'] for d in data]

            c.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            return True
        else:
            raise ValueError(f'load_data: `data` must be of type list[dict] and must contains the following keys in each dict: document, metadata and id')

    def query(self, query_texts: list[str], k: float, where: dict = {}, where_doc: dict = {}, 
              collection: Collection = None, collection_name: str = '', include: list[str] =["documents"] ):
        """
        Query a Chroma collection with the specified query texts. Either pass collection or collection_name. [Full docs about where and where_doc clause](https://docs.trychroma.com/usage-guide#using-where-filters)

        Args:
            query_texts (list[str]): A list of query texts to search for.
            k (float): The number of results to retrieve for each query text.
            where (dict, optional): A dictionary specifying metadata field-value pairs to filter the search results. Defaults to {}.
            where_doc (dict, optional): A dictionary specifying conditions to filter documents based on their contents. Defaults to {}.
            collection (chromadb.Collection, optional): The collection to query. If not provided, a collection with the specified name will be retrieved. Defaults to None.
            collection_name (str, optional): The name of the collection to query if `collection` is not provided. Defaults to ''.
            include (list[str], optional): A list of fields to include in the returned results. Possible values are 'embeddings', 'documents', 'metadatas', and 'distances'. Defaults to ["documents"].

        Returns:
            list: A list of search results. Each search result is a dictionary containing information about the retrieved items, including the documents, metadata, and distances (if applicable).

        Raises:
            ValueError: If the dimensions of the query embeddings do not match those of the collection.

        Examples:
            # Query the collection with a list of query texts
            results = query(
                query_texts=["doc10", "thus spake zarathustra"], 
                k=10, 
                where={"metadata_field": "is_equal_to_this"},
                where_doc={"$contains":"search_string"}, 
                collection_name="my_collection", 
                include=["documents"]
            )
        """
        if not collection:
            collection = self.get_collection(name=collection_name, create_if_fail=False)
        
        if len(query_texts) == 0:
            return 

        return collection.query(
            query_texts=query_texts,
            n_results=k,
            where=where,
            where_document=where_doc,
            include=include
        )

    def get_doc_by_id(self, ids: list[str], collection: Collection = None, collection_name: str = '', where: dict = {}, include: list[str] =["documents"]):
        """
        Retrieve documents from a Chroma collection by their IDs.

        Args:
            ids (list[str]): A list of unique identifiers for the documents to be retrieved.
            collection (Collection, optional): The collection from which to retrieve the documents. If not provided, a collection will be obtained based on the given collection_name. Defaults to None.
            collection_name (str, optional): The name of the collection from which to retrieve the documents. Defaults to ''.
            where (dict, optional): A dictionary specifying additional filters to apply during retrieval based on metadata associated with the documents. Defaults to {}.
            include (list[str], optional): A list specifying which data fields to include in the returned documents. Defaults to ["documents"].

        Returns:
            list[dict]: A list of dictionaries representing the retrieved documents. Each dictionary contains the specified data fields (e.g., 'documents', 'metadatas', etc.).

        Examples:
            # Retrieve documents by their IDs
            docs = get_doc_by_id(ids=["id1", "id2", "id3"], collection_name="my_collection", include=["documents", "metadatas"])
        """
        if not collection:
            collection = self.get_collection(name=collection_name, create_if_fail=False)

        if len(ids) == 0:
            return 
        
        return collection.get(
            ids=ids,
            where=where,
            include=include
        )

    def update_data(self, ids: list[str], metadatas: list[dict] = [], docs: list[str] = [], collection: Collection = None, collection_name: str = ''):
        """
        Update data in a Chroma collection.

        Args:
            ids (list[str]): A list of unique identifiers for the documents to be updated.
            metadatas (list[dict], optional): A list of dictionaries containing metadata associated with the documents to be updated. Defaults to an empty list.
            docs (list[str], optional): A list of document contents to update. Defaults to an empty list.
            collection (Collection, optional): The collection in which to update the data. If not provided, a collection will be obtained based on the given collection_name. Defaults to None.
            collection_name (str, optional): The name of the collection in which to update the data. Defaults to ''.

        Returns:
            None

        Examples:
            # Update data in a collection
            update_data(ids=["id1", "id2", "id3"], metadatas=[{"chapter": "3", "verse": "16"}, {"chapter": "3", "verse": "5"}, {"chapter": "29", "verse": "11"}], docs=["doc1", "doc2", "doc3"], collection_name="my_collection")
        """
        if not collection:
            collection = self.get_collection(name=collection_name, create_if_fail=False)

        collection.upsert(
            ids=ids,
            metadatas=metadatas,
            documents=docs,
        )
    
    def delete_data(self, ids: list[str], where: dict = {}, where_doc: dict = {}, collection: Collection = None, collection_name: str = ''):
        """
        Delete data from a Chroma collection.

        Args:
            ids (list[str]): A list of unique identifiers for the documents to be deleted.
            where (dict, optional): A dictionary specifying additional filters to apply when deleting documents. Defaults to an empty dictionary.
            where_doc (dict, optional): A dictionary specifying additional filters to apply when deleting documents based on their contents. Defaults to an empty dictionary.
            collection (Collection, optional): The collection from which to delete the data. If not provided, a collection will be obtained based on the given collection_name. Defaults to None.
            collection_name (str, optional): The name of the collection from which to delete the data. Defaults to ''.

        Returns:
            None

        Examples:
            # Delete data from a collection
            delete_data(ids=["id1", "id2", "id3"], where={"chapter": "20"}, collection_name="my_collection")
        """
        if not collection:
            collection = self.get_collection(name=collection_name, create_if_fail=False)
        
        collection.delete(
            ids=ids,
            where=where,
            where_document=where_doc
        )


