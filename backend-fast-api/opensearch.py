from opensearchpy import helpers, RequestError, TransportError, OpenSearch
from json import load
from lib_ import aws
from json import load
from requests.exceptions import Timeout

from costant import *

class opensearch_data_handler:
    def __init__(self) -> None:
        self.client = aws().get_opensearch() 
        self.OPENSEARCH_INDEX_NAME = OPENSEARCH_INDEX_NAME

    def load_data_from_json(self):
        """Yields data from json file."""
        filename = 'db.json'
        with open(filename, "r", encoding='utf-8') as f:
            data = load(f)
            print("Data is being ingested...")
            for x, recipe in enumerate(data):
                recipe['category_en'] = recipe['category_en'].replace('_', ' ')
                if recipe['text_en'] == '':
                    recipe['text_en'] = recipe['category_en'] 
                if recipe['text'] == '':
                    recipe['text'] = recipe['category'] 
                yield {"_index": OPENSEARCH_INDEX_NAME, '_id': x, "_source": recipe}            

    def load_data(self):
        """Send multiple data to an OpenSearch client."""

        data = self.load_data_from_json()
        print(f"Ingesting {OPENSEARCH_INDEX_NAME} data")
        response = helpers.bulk(self.client, data, request_timeout=300)
        
        print(f"Data sent to your OpenSearch.")
        return True

    def empty_index(self):
        query_body = {
            "query": {
                "match_all": {}
            }
        }

        # Perform the delete by query request
        response = self.client.delete_by_query(index=OPENSEARCH_INDEX_NAME, body=query_body)

        # Check the response
        if len(response["failures"]) > 0:
            return False

        return True

    def neural_search(self, client: OpenSearch, index_name: str = '', query_body: str = ''):
        """
        Perform a neural search query on the specified OpenSearch index.

        Args:
            client (OpenSearch): The OpenSearch client object used to perform the search.
            index_name (str): The name of the index to search. Defaults to the configured NIVOLA_TEXT_INDEX if not provided.
            query_body (str): The query body in JSON format for the search request.

        Returns:
            dict: The response from the search query.

        Notes:
            This function performs a neural search query on the specified OpenSearch index using the provided query_body.
            If no index_name is provided, it defaults to the configured NIVOLA_TEXT_INDEX.
            The function returns the response from the search query.
            Error handling is implemented for RequestError, TransportError, and Timeout exceptions, with specific handling
            for x_content_parse_exception errors.
        """
        if index_name == '': index_name = self.OPENSEARCH_INDEX_NAME
        try:
            response = client.search(index=index_name, body=query_body)
        # TODO try to test error handling
        except RequestError as e:
            if e.error == "x_content_parse_exception":
                raise Exception(f"Error: {e.info['error']['root_cause'][0]['reason']}")
            else:
                raise Exception(f"RequestError: {e.info}")
        except TransportError as e:
            raise Exception(f"HTTP Error: {e.status_code}, {e.error}")
        except Timeout:
            raise Exception("Timeout error occurred while making the request.")

        return response

    def search_by_text_en(self, question: str, k: int = 9):
        '''
        Retrieve the top ``K`` documents semantically similar to ``question`` based on ``text_en`` field in a kNN index.

        Return:
            A collection of documents
        '''
        query_body = \
        '''{
            "_source": { "exclude": [ "category_en_embedding", "text_en_embedding", "text_it_embedding"] },
            "query": {
                "neural": {
                "text_en_embedding": {
                    "query_text": "'''+question+'''",
                    "model_id": "mXgYKo8BlLTTsnWvtjbF",
                    "k":'''+str(k)+'''
                }
                }
            }
            }
        '''
        return self.neural_search(client=self.client, query_body=query_body)

    def search_by_text_it(self, question: str, k: int = 9):
        '''
        Retrieve the top ``K`` documents semantically similar to ``question`` based on ``text_it`` field in a kNN index.

        Return:
            A collection of documents
        '''
        query_body = \
        '''{
            "_source": { "exclude": [ "category_en_embedding", "text_en_embedding", "text_it_embedding"] },
            "query": {
                "neural": {
                "text_it_embedding": {
                    "query_text": "'''+question+'''",
                    "model_id": "mXgYKo8BlLTTsnWvtjbF",
                    "k":'''+str(k)+'''
                }
                }
            }
            }
        '''
        return self.neural_search(client=self.client, query_body=query_body)

    def search_by_category_en(self, question: str, k: int = 9):
        '''
        Retrieve the top ``K`` documents semantically similar to ``question`` based on ``category_en`` field in a kNN index.

        Return:
            A collection of documents
        '''
        query_body = \
        '''{
            "_source": { "exclude": [ "category_en_embedding", "text_en_embedding", "text_it_embedding"] },
            "query": {
                "neural": {
                "category_en_embedding": {
                    "query_text": "'''+question+'''",
                    "model_id": "mXgYKo8BlLTTsnWvtjbF",
                    "k":'''+str(k)+'''
                }
                }
            }
            }
        '''
        return self.neural_search(client=self.client, query_body=query_body)

def test():
    h = opensearch_data_handler()
    # h.load_data()
    # gg = h.empty_index(); print(gg)
    # h.load_data()
    res = h.search_by_text_en('Ei yo wassup man', 9); print(res)

if __name__ == '__main__':
    pass

