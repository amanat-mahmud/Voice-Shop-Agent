import streamlit as st
from streamlit_mic_recorder import mic_recorder
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

st.set_page_config(page_title="Ecom Bot", page_icon="🛍️", layout="wide")
st.title("🛍️ Ecom Bot")
st.title("Ecom Bot")

# Initialize session state for messages
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# Display message history 
for message in st.session_state.messages:
    with st.chat_message(message['role']):
        st.markdown(message['content'])

# Create columns for text input and mic button


with st._bottom:
    col1, col2 = st.columns([6, 1], vertical_alignment="bottom")
    with col1:
        query = st.chat_input("Write your query")

    with col2:
        st.write("")  # Add some spacing
        audio = mic_recorder(
            start_prompt="🎤",
            stop_prompt="⏹️", 
            just_once=False,
            use_container_width=True,
            key='recorder'
        )

# Handle voice input
# Handle voice input with Whisper
voice_query = None
if audio is not None:
    try:
        import whisper
        import tempfile
        import os
        
        # Load Whisper model (do this once, maybe outside the function)
        model = whisper.load_model("base")
        
        # Save audio to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_file:
            tmp_file.write(audio['bytes'])
            tmp_file_path = tmp_file.name
        
        # Transcribe audio
        result = model.transcribe(tmp_file_path)
        voice_query = result["text"]
        st.toast(f"Voice recognized: {voice_query}")
        
        # Clean up
        os.unlink(tmp_file_path)
        
    except Exception as e:
        st.error(f"Could not process voice input: {e}")
        voice_query = None

# Process query (either text or voice)
current_query = query or voice_query

if current_query:
    # Determine input method for display
    if voice_query and not query:
        query_display = f"🎤 {current_query}"
        input_method = "voice"
    else:
        query_display = current_query
        input_method = "text"
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(query_display)
    st.session_state.messages.append({"role": "user", "content": query_display})

    # Get and display response
    response = ask(current_query)
    with st.chat_message("assistant"):
        st.markdown(response)

    st.session_state.messages.append({"role": "assistant", "content": response})
