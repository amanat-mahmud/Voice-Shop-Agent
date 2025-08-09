import streamlit as st
from faq import create_faq_collection, faq_chain
from product import sql_chain 
from pathlib import Path
from router import router

project_root = Path(__file__).resolve().parent.parent
faqs_path = project_root / "resources" / "faq_data.csv"
create_faq_collection(faqs_path)


def ask(query):
    route = router(query).name
    if route == 'faq':
        return faq_chain(query)
    elif route == 'sql':
        return sql_chain(query)
    else:
        return "I can only assist with e-commerce questions."

st.title("Daraz Bot")

query = st.chat_input("Write your query")

## initialize session state for messages
if "messages" not in st.session_state:
    st.session_state["messages"] = []

## creating message history 
for message in st.session_state.messages:
    with st.chat_message(message['role']):
        st.markdown(message['content'])

if query:
    with st.chat_message("user"):
        st.markdown(query)
    st.session_state.messages.append({"role":"user", "content":query})

    response = ask(query)
    with st.chat_message("assistant"):
        st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})


