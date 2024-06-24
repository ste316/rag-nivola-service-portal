from os import getcwd
from os.path import join

CACHE_DB_PATH = join(getcwd(), 'cache', 'cache.db')
CONVERSATION_DB_PATH = join(getcwd(), 'session_data', 'conversation.db')
CACHE_EXP_DAY = 30
OPENSEARCH_INDEX_NAME = 'test_all_mini_cosine'