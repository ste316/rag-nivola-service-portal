from prompts import *
from lib_ import util, aws
from deepl import Translator
from xml.dom.minidom import parseString
from costant import *
from db_cache import cache_db
from db_chat import conversation_db
from opensearch import opensearch_data_handler
from json import dumps, loads
from os.path import exists
from re import sub, findall, DOTALL

class rag:
    def __init__(self, debug_mode: bool = False, lang: str = 'en') -> None:
        self.debug_mode = debug_mode
        lang = lang.lower()
        if lang not in ['en', 'it']: raise Exception('rag.__init__: invalid lang, supported lang: EN, IT')
        else: self.lang = lang

        self.settings = util.load_settings()
        self.aws = aws(load_bedrock=True, load_opensearch=False)
        self.bedrock = self.aws.bedrock
        self.opensearch = opensearch_data_handler()
        self.cache_handler = cache_db()
        self.chat_handler = conversation_db()

    def translate(self, query: str, target_lang: str = 'EN-US'):
        translator = Translator(self.settings['deepl_api'])

        result = translator.translate_text(query, target_lang=target_lang)
        if self.debug_mode: print(result.text)
        return result.text

    def launch_searches(self, question: str, k: int = 11):
        res_1 = self.unpack_query_result(self.opensearch.search_by_text_en(question=question, k=k))
        res_2 = self.unpack_query_result(self.opensearch.search_by_text_it(question=question, k=k))
        res_3 = self.unpack_query_result(self.opensearch.search_by_category_en(question=question, k=k))
        return res_1, res_2, res_3

    def extract_hash_from_result(self, res: list[dict]) -> set[str]:
        return set(record['hash'] for record in res)

    def sort_objects_by_score(self, objects: list) -> list:
        """
        Sort a list of objects based on the '_score' value in descending order.

        Args:
            objects (list): The list of objects to be sorted.

        Returns:
            list: The sorted list of objects.
        """
        sorted_objects = sorted(objects, key=lambda x: x['_score'], reverse=True)
        return sorted_objects

    def search_doc(self, question: str, only_3of3: bool = False, k: int = 11) -> list[dict]:
        '''
        Return the docs that exist in at least 2/3 of the result sets
        This means docs that exist in:
        - 3 out of 3 sets
        - 2 out of 3 sets
        are returned as list of dict
        '''
        res_1, res_2, res_3 = self.launch_searches(question=question, k=k)
        all_res = res_1 + res_2 + res_3

        # Create sets of hashes from each set of records
        hash_set_1 = set(record['_source']['hash'] for record in res_1)
        hash_set_2 = set(record['_source']['hash'] for record in res_2)
        hash_set_3 = set(record['_source']['hash'] for record in res_3)

        # Find the docs in common in all 3 searches
        hash_in_3of3 = hash_set_1.intersection(hash_set_2, hash_set_3)

        if not only_3of3:
            # Find the union of pairs of sets
            union_12 = hash_set_1.union(hash_set_2)
            union_23 = hash_set_2.union(hash_set_3)
            union_31 = hash_set_3.union(hash_set_1)

            # Find the intersection of pairs of sets
            intersection_12_3 = union_12.intersection(hash_set_3)
            intersection_23_1 = union_23.intersection(hash_set_1)
            intersection_31_2 = union_31.intersection(hash_set_2)

            # Find Symmetric Difference of Intersections
            intersection_12_3_23 = intersection_12_3.symmetric_difference(intersection_23_1)
            intersection_12_3_31 = intersection_12_3.symmetric_difference(intersection_31_2)

            # Combine both symmetric differences to get the final selected set of hashes
            hash_in_2of3 = intersection_12_3_23.union(intersection_12_3_31)
            selected_hashes = hash_in_2of3.union(hash_in_3of3)
        else:
            selected_hashes = hash_in_3of3

        # Filter records that have hashes present in the selected hashes
        
        selected_records = [{'_score': record['_score'], **record['_source']} for record in all_res if record['_source']['hash'] in selected_hashes]
        # delete duplicate, by default there are duplicates because docs must be in 2 or 3 results sets, therefore the are for sure 2 or 3 duplicate docs
        unique_res = self.get_unique_output(selected_records, selected_hashes) 
        # unique output randomly mixes the docs order, but we want it to be in order of score
        unique_res = self.sort_objects_by_score(unique_res)
        if self.debug_mode: print(len(unique_res)); print(unique_res)

        return unique_res

    def get_unique_output(self, L: list[dict], LK: set[str]) -> list[dict]:
        """
        Retrieve unique objects from a list based on matching hash attributes with values in LK.

        Args:
            L (list[dict]): A list of dictionaries representing objects.
            LK (set[str]): A set of unique keys linked to the 'hash' attribute of the objects.

        Returns:
            list[dict]: A list containing unique objects whose hash attributes match keys in LK.
        """
        # Initialize the list to store unique objects
        O = []

        # Initialize a set to keep track of added hashes
        added_hashes = set()

        # sort the result, in order to take only the highest scores, across all 3 response
        # (the are duplicate record BUT with different score, we are interested in the first one) 
        L = self.sort_objects_by_score(L)

        # Iterate through the list L
        for obj in L:
            # Check if the hash attribute of the object matches any key in LK
            if obj['hash'] in LK:
                # Check if the hash of the object has not been added before
                if obj['hash'] not in added_hashes:
                    # Add the object to the list O
                    O.append(obj)
                    # Add the hash of the object to the set of added hashes
                    added_hashes.add(obj['hash'])

        # O now contains a list of unique objects
        return O

    def unpack_query_result(self, query_res: str) -> dict:
        return dict(query_res)['hits']['hits']

    def common_hashes(self, set1: set, set2: set, set3: set) -> set:
        """
        Find the common hashes among three sets.

        Args:
            set1 (set): The first set of hashes.
            set2 (set): The second set of hashes.
            set3 (set): The third set of hashes.

        Returns:
            set: The set of common hashes.
        """
        return set1 & set2 & set3
    
    def get_full_record_by_hashes(self, selected_hashes: set[str], all: list[dict]) -> list[dict]:
        selected_records = [record for record in all if record['hash'] in selected_hashes]
        return selected_records

    def beautify_xml(self, xml_string: str) -> str:
        # Parse the XML string
        dom = parseString(xml_string)
        # Serialize the parsed XML back to a formatted string
        beautified_xml = dom.toprettyxml(indent=" "*4)
        # Remove the XML declaration
        beautified_xml = beautified_xml.replace('<?xml version="1.0" ?>\n', '')
        return beautified_xml

    def log_similarity_scores(self, question: str, score_list: list[float], texts: list[str], chat_id: str):

        def delete_simil_score_from_text(input_string: str):
            # Define the pattern to match
            pattern = r'\s*similarity="[^"]*"'

            # Use re.sub() to replace the matched pattern with an empty string
            return sub(pattern, '', input_string)
        
        if len(score_list) != len(texts):
            raise Exception('analyze_similarity_scores: len(score_list) MUST be EQUAL len(texts) ')
        
        self._log_curr_message_id = chat_id + '-' + util.generate_random_string(10) # change for every new message
        file_path = 'simil-score.json'
        if not exists(file_path):
            # Create the file if it doesn't exist
            with open(file_path, "w", encoding='utf-8') as file:
                file.write(dumps([]))
                input()

        data = []
        for i, score in enumerate(score_list):
            data.append({
                'id': self._log_curr_message_id,
                'doc': delete_simil_score_from_text(texts[i]),
                'score': score,
                'question': question
            })
        # print(data)
        previuos_data: list = loads(open(file_path, 'r', encoding='utf-8').read())
        previuos_data.extend(data)
        open(file_path, 'w', encoding='utf-8').write(dumps(previuos_data, indent=4, ensure_ascii=False))

    def log_claude_res(self, answer: str):
        file_path = 'simil-score.json'

        previuos_data: list = loads(open(file_path, 'r', encoding='utf-8').read())
        new_data = []
        for obj in previuos_data:
            if obj['id'] == self._log_curr_message_id:
                obj['answer'] = answer
        
            new_data.append(obj)
        
        open(file_path, 'w', encoding='utf-8').write(dumps(new_data, indent=4, ensure_ascii=False))

    def get_similar_docs(self, query_text: str, chat_id: str):
        chat_docs = dict()
        chat_docs_link = dict()
        cache_docs_used = dict()
        ##### for score analysis
        score_list = []
        text_list = []

        similar_docs = self.search_doc(question=query_text, only_3of3=True) 

        for obj in similar_docs:
            score_list.append(obj['_score'])
            additional_data = ''
            if len(obj['required_role']):
                additional_data += f'<required-role>{",".join(obj['required_role'])}</required-role>'
            
            if self.lang == 'en':
                data = f"<doc similarity=\"{obj['_score']}\"><category>{obj['category_en']}</category><text>{obj['text_en']}</text>{additional_data}</doc>"
            else:
                data = f"<doc><category>{obj['category']}</category><text>{obj['text']}</text>{additional_data}</doc>"
            cache_docs_used[obj['hash']] = {
                'data': data,
                'link': obj['link'],
                'category': obj['category_en'],
                'positive_vote': 0,
                'negative_vote': 0,
                'time_used': 1
            }
            docs_text = self.beautify_xml(data)
            chat_docs[obj['hash']] = {
                'data': docs_text
            }
            text_list.append(docs_text)
            chat_docs_link[obj['hash']] = obj['link']
        
        self.log_similarity_scores(query_text, score_list, text_list, chat_id)

        return chat_docs, chat_docs_link, cache_docs_used

    def get_most_usefull_doc_link(self, answer: str, docs_link: dict) -> str:
        try:
            if '<most-usefull-doc>' in answer and '</most-usefull-doc>' in answer:
                doc_id_pattern = r'<most-usefull-doc>(.*?)<\/most-usefull-doc>'
                doc = findall(doc_id_pattern, answer, DOTALL)[0].strip()

                return docs_link[doc]
        except:
            pass

        return ''

    def exec_rag(self, query_text: str, chat_id: str, custom_system_prompt: str):
        self.chat_handler.get_or_create_chat(chat_id) # create the chat
        chat_docs, chat_docs_link, _ = self.get_similar_docs(query_text, chat_id) # retrieve docs from Vector DB
        # print(chat_docs)
        # self.cache_handler.add_new(cache_docs_used)

        chat_docs = self.chat_handler.add_docs(chat_id, chat_docs) # add retrieved docs to the conversation storage
        new_msg = [{ 
                "role": "user",  # create the new message to send to update the conversation
                "content": query_text
            }
        ]

        if not self.chat_handler.add_message(chat_id, new_msg): # add new message to the conversation storage
            raise Exception('Unable to add new msg from User')
        
        messages = list(self.chat_handler.get_or_create_chat(chat_id)) # ri-retrieve messages
        messages[-1]['content'] = USER_PROMPT.format(docs=chat_docs, question=query_text) # add all related docs to the last messages; the one that will be sent to Claude
        
        response = self.aws.call_claude_3(system_prompt=custom_system_prompt, messages=messages, bedrock_runtime=self.bedrock)

        self.log_claude_res(response)
        if not self.chat_handler.add_message(chat_id, [{
            'role': 'assistant', # add response to the converdation storage
            'content': response
        }]):
            raise Exception('Unable to add new msg from Assistant')

        # if self.debug_mode: open('log-claude.json', 'a', encoding='utf-8').write(f'\n{"*"*30}\n{dumps(self.chat_handler.get_conversation(chat_id)['docs'], indent=4, ensure_ascii=False)}')
        return response

    def public_exec_rag(self, question: str, chat_id: str):
        return self.exec_rag(question, chat_id, SYS_CLAUDE_ASSISTANT_NIVOLA_NEW)

    def public_create_empty_chat(self) -> str:
        chat_id = util.generate_random_string(20)
        self.chat_handler.get_or_create_chat(chat_id)

        return chat_id

if __name__ == '__main__':
    # lang = input('choose "en" or "it": ').strip()
    r = rag()
    question = input('Ask me anything about Nivola\n')
    chat_id = util.generate_random_string()
    while True:
        res = r.exec_rag(question, chat_id, SYS_CLAUDE_ASSISTANT_NIVOLA_NEW)
        question = input(res)
        if question.strip().lower() == 'q':
            print(f'Chat closed, chat_id = {chat_id}')
            exit()
