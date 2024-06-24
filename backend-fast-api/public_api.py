from main import rag
from fastapi import FastAPI
from re import findall, DOTALL, sub, search

app = FastAPI()
RAG = rag(False, 'en')

def deep_space_clean(text: str):
    for _ in range(3): text = sub(r'\s+', ' ', text)

def no_xml_tags(text: str) -> bool:
    """
    Check if a given string contains no XML-like tags.

    Args:
        text (str): The input string to check.

    Returns:
        bool: True if there are no XML-like tags, False otherwise.
    """
    # Define the regex pattern to match XML-like tags
    pattern = r'<[^>]+>'
    
    # Search for any matches of the pattern in the text
    match = search(pattern, text)
    
    # Return True if no tags are found, False otherwise
    return match is None

@app.get("/")
def read_root():
    return 'Alo'

@app.get("/new_chat")
def new_chat() -> dict:
    '''
    Create a new chat, return the chat_id

    chat_id can be utilized in /send_message
    '''
    res = {
        'answer': RAG.public_create_empty_chat()
    }
    return res

@app.post("/send_message")
def send_message(question: str, chat_id: str) -> dict:
    '''
    Ask question about Nivola
    '''
    answer = RAG.public_exec_rag(question, chat_id)
    print(answer)
    question = deep_space_clean(question)
    res = {
        'answer': 'Generic Error'
    }

    try:
        if no_xml_tags(answer):
            res['answer'] = answer
            return res
        
        if '<final-answer>' in answer and '</final-answer>' in answer:
            # Define the regex pattern to extract the text inside <final-answer> tag
            pattern = r'<final-answer>(.*?)<\/final-answer>'
        
            # Use re.findall() to find all matches of the pattern
            matches = findall(pattern, answer, DOTALL)
            if matches:
                res['answer'] = matches[0].strip()
                return res
            else:
                filename = 'log-error.log'
                log = f'send_message: {chat_id=} no answer found, check log in {filename}'
                print(log)
                open(filename, 'a', encoding='utf-8').write(f'send_message | {chat_id} | {answer}')
    except Exception:
        res['answer'] = 'Error while parsing Response...'
        return res
    
    return res

@app.get('/get_all_conversation')
def get_all_conversation() -> str:
    '''
    return all conversation from the db
    '''
    return RAG.chat_handler.get_all_conversation()

@app.get('/get_conversation')
def get_conversation(chat_id: str):
    '''
    return one conversation with id: chat_id
    '''
    return RAG.chat_handler.get_conversation(chat_id)

