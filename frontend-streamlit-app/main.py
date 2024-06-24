import streamlit as st
from pathlib import Path
from os import makedirs

makedirs('pages', exist_ok=True)

st.set_page_config(
    page_title="Nivola Assistant",
    page_icon="☁️",
)

st.title("Nivola Assistant")
# Create sidebar elements
st.markdown("#### Create New Chats")

page_name = st.text_input("insert page name", placeholder='Page Name', label_visibility='hidden')

if page_name and st.button("Create new page"): 
    st.session_state[page_name] = {}
    (Path("pages") / f"{page_name}.py").write_text(
"""
import streamlit as st
import requests as r
BASE_URL = 'http://localhost:8000/'

page_name = '"""+page_name+"""'

st.set_page_config(
    page_title=f"Nivola Assistant - {page_name}",
    page_icon="☁️",
)

def new_chat() -> str:
    endpoint = 'new_chat'
    res = r.get(BASE_URL+endpoint)
    print(res.text)
    return res.json()['answer']

def send_message(question: str) -> str:
    endpoint = 'send_message'
    if 'chat_id' not in st.session_state[page_name]:
        st.session_state[page_name]['chat_id'] = new_chat()

    print(f'send_message: {question=} {st.session_state[page_name]["chat_id"]=}')

    data = {
        'question': question['content'],
        'chat_id': st.session_state[page_name]["chat_id"]
    }
    res = r.post(BASE_URL+endpoint, params=data) # , params=data
    print(res.text)
    return res.json()['answer']

st.title("Ask me anything about Nivola Services!")

if 'chat_id' not in st.session_state[page_name]:
    st.session_state[page_name]['chat_id'] = new_chat()

# create message list
if "messages" not in st.session_state[page_name]:
    st.session_state[page_name]['messages'] = []

for message in st.session_state[page_name]['messages']:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("What is up?"):
    st.session_state[page_name]['messages'].append({"role": "user", "content": prompt})
    print(st.session_state[page_name]['messages'])

    with st.chat_message("user"):
        st.markdown(prompt)

    answer = ''
    with st.spinner("Thinking..."):
        answer = send_message(st.session_state[page_name]['messages'][-1])

    with st.chat_message("assistant"):
        response = st.write(answer)

    st.session_state[page_name]['messages'].append({"role": "assistant", "content": answer})
""",
        encoding="utf-8",
    )



