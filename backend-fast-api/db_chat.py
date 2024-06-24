from sqlite3 import connect
from typing import List, Dict
from dataclasses import dataclass
from json import dumps, loads
from costant import *
from lib_ import aws, util

@dataclass
class Message:
    """
    Represents a message in a conversation with a role (user or assistant) and content.

    Attributes:
        role (str): The role of the message sender, either 'user' or 'assistant'.
        content (str): The content of the message.
    """
    role: str
    content: str

    def __post_init__(self):
        """
        Perform post-initialization checks on the Message object.

        Raises:
            AssertionError: If role is not 'user' or 'assistant', or if content is an empty string.
        """
        # Convert role to lowercase
        self.role = self.role.lower()

        # Check role is a non-empty string
        assert isinstance(self.role, str) and self.role.lower() in ['user', 'assistant'], "Role must be either 'user' or 'assistant'"
        
        # Check content is a non-empty string
        assert isinstance(self.content, str) and self.content.strip(), "Content must be a non-empty string"

    def to_dict(self) -> dict:
        """
        Convert Message object to a dictionary.

        Returns:
            dict: A dictionary representation of the Message object with 'role' and 'content' keys.
        """
        return {
            'role': self.role,
            'content': self.content
        }

    def to_list(self) -> list:
        """
        Convert Message object to a list.

        Returns:
            list: A list representation of the Message object.
        """
        return [self.role, self.content]

    def __iter__(self):
        """
        Make the Message object iterable.

        Yields:
        - tuple: The key-value pairs of the Message object.
        """
        yield 'role', self.role
        yield 'content', self.content
    
    @classmethod
    def from_dict(cls, dict_message: dict):
        if set(dict_message.keys()) == set(['content', 'role']):
            return cls(dict_message['role'], dict_message['content'])
        
        raise ValueError('dict_message must only contains "role" and "content" keys')

@dataclass
class Docs:
    """
    Represents a collection of documents.

    Attributes:
        data (Dict[str, dict]): A dictionary where the keys are document hashes and the values are dictionaries representing document contents.
    """
    data: Dict[str, dict]

    def __post_init__(self):
        """
        Perform post-initialization validation checks.
        
        Raises:
            ValueError: If the data attribute is not a dictionary or if any key or value in the data dictionary is not of the correct type.
        """
        self.__are_valid__()

    def __are_valid__(self):
        """
        Check if the data attribute is a valid dictionary with appropriate types for keys and values.

        Raises:
            ValueError: If the data attribute is not a dictionary or if any key or value in the data dictionary is not of the correct type.
        """
        if not isinstance(self.data, dict):
            raise ValueError("Data must be a dictionary")
        
        for key, value in self.data.items():
            if not isinstance(key, str):
                raise ValueError("Keys in the data dictionary must be strings")
            if not isinstance(value, dict):
                raise ValueError("Values in the data dictionary must be dictionaries")

    def to_dict(self) -> dict:
        """
        Convert the Docs object to a dictionary.

        Returns:
            dict: A dictionary representation of the Docs object.
        """
        return {"data": self.data}

    @classmethod
    def from_dict(cls, data: dict):
        if 'data' in data.keys():
            data = data['data']

        return cls(data)

    @classmethod
    def from_str(cls, data: str):
        return cls.from_dict(loads(data))

    def get_doc_keys(self) -> list:
        """
        Get the keys (document hashes) from the data dictionary.

        Returns:
            List[str]: A list containing the keys (document hashes) from the data dictionary.
        """
        return list(self.data.keys())

    def get_doc_values(self) -> list:
        """
        Get the values (document contents) from the data dictionary.

        Returns:
            List[dict]: A list containing the values (document contents) from the data dictionary.
        """
        return list(self.data.keys())

    def __iter__(self):
        """
        Make the Docs object iterable over its data attribute.

        Returns:
            iter: An iterator over the items of the data dictionary.
        """
        return iter(self.data.items())

    def __dict__(self):
        """
        Get the data attribute as a dictionary.

        Returns:
            dict: The data attribute.
        """
        return self.data

    def to_string(self) -> str:
        """
        Convert the Docs object to a JSON string.

        Returns:
            str: A JSON string representation of the Docs object.
        """
        return dumps(self.to_dict(), indent=4)

    def __str__(self) -> str:
        """
        Convert the Docs object to a JSON string.

        Returns:
            str: A JSON string representation of the Docs object.
        """
        return dumps(self.to_dict(), indent=4)

    def add_data(self, ids: list[str], contents: list[dict]) -> bool:
        """
        Add new document data to the Docs object.

        Args:
            ids (List[str]): List of document hashes to add.
            contents (List[dict]): List of dictionaries representing document contents to add.

        Returns:
            bool: True if the data is successfully added, False otherwise.

        Raises:
            ValueError: If the length of ids does not match the length of contents.
        """
        if len(ids) != len(contents):
            raise ValueError('ids length must match contents length')
        
        for index, id in enumerate(ids):
            if id not in self.get_doc_keys():
                self.data[id] = contents[index]
        
        self.__are_valid__()
        return True

@dataclass
class Conversation:
    """
    Represents a conversation consisting of a list of messages.

    This class provides functionality to manage and manipulate conversations, including adding messages,
    checking message consistency, converting to various formats, and creating from a JSON string.

    Attributes:
        messages (List[Message]): A list of Message objects representing the conversation's messages.

    Dependencies:
        - Message: Represents individual messages within the conversation.

    Methods:
        - add_message(addition_msg: List[Message]) -> bool: Extend the messages of the Conversation object with additional messages.
        - to_list() -> list[dict]: Convert Conversation object to a list of dictionaries.
        - to_dict() -> dict: Convert Conversation object to a dictionary.
        - to_string() -> str: Convert Conversation object to a JSON data string.
        - from_string(str_conversation: str) -> Conversation: Create a Conversation object from a JSON string.
    """
    messages: List[Message]

    def __post_init__(self):
        """
        Perform post-initialization checks on the Conversation object.

        Raises:
            AssertionError: If the list of messages is not consistent.
        """
        # Check messages is a list containing only Message objects
        self.__is_list_of_message(self.messages)
        self.__are_msg_consistent(self.messages)

    def __is_list_of_message(self, messages):
        """
        Check if the input is a list of Message objects.

        Args:
            messages: Input to be checked.

        Raises:
            AssertionError: If the input is not a list or if any element in the list is not a Message object.
        """
        assert isinstance(messages, list), "Messages must be a list"
        for msg in messages:
            assert isinstance(msg, Message), "Each message must be a Message object"

    def __are_msg_consistent(self, messages: list[Message]):
        """
        Check if the messages in the list are consistent according to specific requirements.

        Args:
        - messages (list[dict]): List of dictionaries representing messages, each containing 'role' and 'content' keys.

        Raises:
            ValueError: If the messages do not meet requirements:
            - The first message must be from the user.
            - The roles must alternate.

        Returns:
            bool: True if the messages are consistent, False otherwise.
        """
        check = True
        messages: list[dict] = self.__to_list(messages)

        if len(messages) == 0:
            return check

        if not messages or messages[0]['role'] != 'user':
            check = False
        
        for i in range(1, len(messages)):
            if messages[i]['role'] == messages[i-1]['role']:
                check = False
        
        if not check:
            raise ValueError(f'requirement not satisfied: messages are not consistent:\n\t- the first message must be from the user\n\t- the roles must alternate')

        return check

    def add_message(self, addition_msg: list[Message]) -> bool:
        """
        Extend the messages of the Conversation object with additional messages.

        Args:
            addition_msg (list[Message]): List of Message objects to add to the Conversation.

        Returns:
            bool: True if the messages are successfully extended.

        Raises:
            AssertionError: If the input is not a list or if any element in the list is not a Message object.
            ValueError: If the messages are not consistent, i.e., if the first message is not from the user or if the roles do not alternate.
        """
        new_msgs = self.messages + addition_msg
        self.__is_list_of_message(new_msgs)

        if self.__are_msg_consistent(new_msgs):
            self.messages = new_msgs
            return True

    def __iter__(self):
        """
        Make the Conversation object iterable.

        Yields:
        - dict: The dictionary representation of each Message object in the Conversation.
        """
        for message in self.messages:
            yield dict(message)

    def __to_list(self, msgs: list[Message]) -> list[dict]:
        """
        Convert a list of Message objects to a list of dictionaries.

        Args:
            msgs (list[Message]): List of Message objects to convert.

        Returns:
            list[dict]: A list of dictionaries representing the messages.
        """
        list_msg = []
        for msg in msgs:
            list_msg.append(msg.to_dict())
    
        return list_msg

    def to_list(self) -> list[dict]:
        """
        Convert Conversation object to a list of dictionaries.

        Returns:
        - list[dict]: A list containing dictionary representations of each message in the Conversation object.
        """
        return [msg.to_dict() for msg in self.messages]
    
    def to_dict(self) -> dict:
        """
        Convert Conversation object to a dictionary.

        Returns:
        - dict: A dictionary representation of the Conversation object.
        """
        return {
            "messages": [message.__dict__ for message in self.messages]
        }
    
    def to_string(self) -> str:
        """
        Convert Conversation object to a json data string.

        Returns:
        - str: A str representation of the Conversation object.
        """
        return dumps(self.to_dict(), indent=4)

    def __str__(self) -> str:
        """
        Convert Conversation object to a json data string.

        Returns:
        - str: A str representation of the Conversation object.
        """
        return dumps(self.to_dict(), indent=4)

    @classmethod
    def from_string(cls, str_conversation: str):
        """
        Create a Conversation object from a JSON string.

        Args:
            str_conversation (str): JSON string representation of the Conversation object.

        Returns:
            Conversation: The Conversation object created from the JSON string.
        """
        # Deserialize the JSON string to a dictionary
        conversation_dict = loads(str_conversation)
        
        # Extract messages from the dictionary and convert them to Message objects
        messages = [Message(**message_dict) for message_dict in conversation_dict["messages"]]
        
        # Create and return a new Conversation object with the extracted messages
        return cls(messages)

class conversation_db:
    """
    ConversationDB represents a database manager for conversations.

    This class manages the storage and retrieval of conversation data in a SQLite database.
    It provides methods to perform various operations such as retrieving, creating, updating, and deleting conversations.

    Dependencies:
        - Conversation: Represents a conversation and its messages.
        - Message: Represents a message within a conversation.
        - Docs: Represents documents associated with a conversation.

    Methods:
        - __init__(): Initialize the ConversationDB object and create the necessary database table if it doesn't exist.

        - get_or_create_chat(conversation_id: str, conversation: Conversation = Conversation([])) -> Conversation:
            Retrieve an existing conversation by its ID from the database, or create a new one if it doesn't exist.

        - get_conversation(conversation_id: str) -> dict:
            Retrieve a conversation and associated documents from the database.

        - get_all_conversation() -> Dict[str, Conversation]:
            Retrieve all conversations from the database.
        
        - get_docs(conversation_id: str) -> Docs or None:
            Retrieve the documents associated with a conversation from the database.

        - add_docs(conversation_id: str, new_docs: dict) -> bool:
            Add new documents to a conversation in the database.

        - add_message(conversation_id: str, new_msg: List[Message] | List[dict]) -> bool:
            Add new messages to an existing conversation in the database.

        - get_multiple_conversations(conversation_ids: List[str]) -> List[Conversation]:
            Retrieve multiple conversations from the database by their IDs.

        - delete_chat(conversation_id: str) -> bool:
            Delete a conversation from the database based on its ID.
    """
    def __init__(self) -> None:
        if not util.create_operational_folder():
            raise Exception('Conversation.__init__: cannot create operational folders')
        self.conn = connect(CONVERSATION_DB_PATH, check_same_thread=False)
        self.cursor = self.conn.cursor()

        self.cursor.execute(
            '''CREATE TABLE IF NOT EXISTS conversation (
                    id TEXT PRIMARY KEY,
                    messages TEXT null,
                    docs TEXT null
                )''')
        
    def get_or_create_chat(self, conversation_id: str, conversation: Conversation = Conversation([])) -> Conversation:
        """
        Retrieve an existing conversation by its ID from the database, or create a new one if it doesn't exist.

        Args:
            conversation_id (str): The ID of the conversation to retrieve or create.
            conversation (Conversation, optional): The Conversation object to create if the conversation does not exist. Defaults to an empty Conversation.

        Returns:
            Conversation: The Conversation object retrieved from the database or created.
        """
        chat = self.get_conversation(conversation_id)
        if not chat:
            self.cursor.execute("INSERT INTO conversation (id, messages) VALUES (?, ?)", (conversation_id, conversation.to_string()))
            self.conn.commit()
            return conversation
        else:
            return chat['chat']

    def get_conversation(self, conversation_id: str) -> dict:
        """
        Retrieve a conversation and associated documents from the database.

        Args:
            conversation_id (str): The ID of the conversation to retrieve.

        Returns:
            dict: A dictionary containing the conversation messages and associated documents if found, otherwise an empty dictionary.
        """
        self.cursor.execute("SELECT messages, docs FROM conversation WHERE id = ?", (conversation_id,))
        row = self.cursor.fetchone()
        if row:
            docs = Docs({})

            if row[1] != None: # if conversation contains documents
                docs = Docs(loads(row[1])) # load them
            
            to_return = {
                'chat': Conversation.from_string(row[0]),
                'docs': docs
            }
            return to_return
        else:
            return {}
    
    def get_all_conversation(self) -> Dict[str, Conversation]:
        """
        Retrieve all conversations from the database.

        Returns:
            Dict[str, Conversation]: A dictionary containing conversation IDs as keys and Conversation objects as values.
        """
        conversations = {}

        self.cursor.execute("SELECT id, messages FROM conversation",)
        rows = self.cursor.fetchall()
        
        for r in rows:
            conversations[r[0]] = Conversation.from_string(r[1])

        return conversations

    def get_docs(self, conversation_id: str) -> Docs:
        """
        Retrieve the documents associated with a conversation from the database.

        Args:
            conversation_id (str): The ID of the conversation for which documents are to be retrieved.

        Returns:
            Docs or None: The Docs object containing the documents associated with the conversation if found, else None.
        """
        self.cursor.execute("SELECT docs FROM conversation WHERE id = ?", (conversation_id))
        row = self.cursor.fetchone()

        if row[0]:
            return Docs.from_str(row[0])
        else:
            return None

    def add_docs(self, conversation_id: str, new_docs: dict) -> Docs:
        """
        Add new documents to a conversation in the database.

        Args:
            conversation_id (str): The ID of the conversation to which new documents will be added.
            new_docs (dict): A dictionary where the keys are document hashes and the values are dictionaries representing document contents.

        Returns:
            bool: True if the documents are successfully added to the conversation and the conversation is updated in the database, False otherwise.
        """
        temp = self.get_conversation(conversation_id)

        if not temp['chat']: # chat not exist
            self.get_or_create_chat(conversation_id) # create the chat without any msg
            old_docs = Docs(new_docs) # create the docs obj
        else:
            ids = list(new_docs.keys())
            contents = list(new_docs.values()) # reorg data to add it
            old_docs: Docs = temp['docs'] # load past docs into variable
            old_docs.add_data(ids, contents) # add new datas
        
        old_docs = dumps(dict(old_docs), indent=4, ensure_ascii=False)

        self.cursor.execute("UPDATE conversation SET docs = ? WHERE id = ?", (old_docs, conversation_id))
        self.conn.commit()
        
        return old_docs

    def add_message(self, conversation_id: str, new_msg: List[Message] | List[dict]):
        """
        Add new messages to an existing conversation in the database.

        Args:
            conversation_id (str): The ID of the conversation to which new messages will be added.
            new_msg (List[Message]): List of Message objects representing the new messages to be added.

        Returns:
            bool: True if the new messages are successfully added to the conversation and the conversation is updated in the database, False otherwise.
        """
        # Retrieve the current conversation
        current_conversation_obj = self.get_conversation(conversation_id)
        
        if current_conversation_obj['chat']:
            current_conversation_obj: Conversation = current_conversation_obj['chat']

            if util.is_dict_list(new_msg):
                new_msg = [Message.from_dict(msg) for msg in new_msg]

            # Add the new messages to the existing messages
            current_conversation_obj.add_message(new_msg)
            # Serialize the updated Conversation object to JSON
            updated_conversation = current_conversation_obj.to_string()
            # Update the conversation in the database
            self.cursor.execute("UPDATE conversation SET messages = ? WHERE id = ?", (updated_conversation, conversation_id))
            self.conn.commit()
            return True
        else:
            print("Conversation not found.")
            return False

    def get_multiple_conversations(self, conversation_ids: List[str]) -> List[Conversation]:
        """
        Retrieve multiple conversations from the database by their IDs.

        Args:
            conversation_ids (List[str]): List of conversation IDs to retrieve.

        Returns:
            List[Conversation]: List of Conversation objects retrieved from the database.
        """
        conversations = []
        for conversation_id in conversation_ids:
            conversation = self.get_conversation(conversation_id)['chat']
            if conversation:
                conversations.append(conversation)
        return conversations

    def delete_chat(self, conversation_id: str) -> bool:
        """
        Delete a conversation from the database based on its ID.

        Args:
            conversation_id (str): The ID of the conversation to delete.

        Returns:
            bool: True if the conversation was successfully deleted, False otherwise.
        """
        # Check if the conversation exists before attempting to delete it
        if self.get_conversation(conversation_id):
            self.cursor.execute("DELETE FROM conversation WHERE id = ?", (conversation_id,))
            self.conn.commit()
            return True
        else:
            return False

    def condense_message(self, aws: aws, id: str, n: int = 5):
        raise Exception('uninplemented...')
        all_msg: list = self.get_conversation(id).messages
        selected_msg = all_msg[-n:]

        # ask claude to condense the selected_msg into one
        # msg = aws.call_claude_3()
        msg = [{}]
        self.delete_chat(id)
        return self.new_chat(id, msg)

def test():
    print('this text func might be outdated')
    # Create a new conversation
    conversation_db_instance = conversation_db()
    conversation_id = "conversation_1"
    conversation_db_instance.delete_chat(conversation_id)
    conversation_db_instance.get_or_create_chat(conversation_id)
    print(f'Conversation: {conversation_id} created!')

    while True:
        q = input('Press ENTER to add a message to the conversation or type Q to quit...')
        if q.lower() == 'q': break

        role = input('\tChoose the role: ')
        content = input('\tChoose the content: ')
        additional_messages = [Message(role, content)]
        conversation_db_instance.add_message(conversation_id, additional_messages)
        print(f'Message successfully added!')

    input('Press ENTER to see the Conversation...')
    
    print('Retrieve multiple conversations by IDs')
    conversation_ids = ["conversation_1", "conversation_2"]  # Example IDs
    multiple_conversations = conversation_db_instance.get_multiple_conversations(conversation_ids)
    print("Retrieved Conversations:")
    for conv in multiple_conversations:
        print(conv.to_string())
    
    # Delete a conversation
    print('Deleting this Test Chat...')
    conversation_to_delete = "conversation_1"  # Example ID
    deleted = conversation_db_instance.delete_chat(conversation_to_delete)
    if deleted:
        print(f"Conversation {conversation_to_delete} deleted successfully.")
    else:
        print(f"Conversation {conversation_to_delete} not found.")

    # Example of condensing messages (not implemented)
    # aws_instance = aws()  # Example AWS instance
    # conversation_db_instance.condense_message(aws_instance, conversation_id, 5)

def test_docs():
    chat_handler = conversation_db()
    # new_docs = Docs()
    convs = chat_handler.get_conversation('test_1')

    if not convs:
        res = chat_handler.add_docs('test_add_docs', {'id3': {'value': 1}, 'id32': {}})
        print(res)
    else:
        print(convs['chat'])
        print(convs['docs'])

if __name__ == '__main__':
    pass
    