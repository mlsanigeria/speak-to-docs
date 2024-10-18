import streamlit as st
import os
import logging
from dotenv import load_dotenv
from src.speech_io import transcribe_audio, synthesize_speech
from src.rag_functions import allowed_files, file_check_num, extract_contents_from_doc
from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI
from langchain.embeddings import OpenAIEmbeddings
import openai
import time

# Set up page configuration
st.set_page_config(page_title="Speak-To-Docs", page_icon="📝", layout="wide", initial_sidebar_state="expanded")

# Configure logging
logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s:%(levelname)s:%(message)s')

# Load environment variables
load_dotenv()

# Session timeout in seconds (e.g., 30 minutes)
SESSION_TIMEOUT = 1800

# Initialize session state variables
if 'last_activity' not in st.session_state:
    st.session_state.last_activity = time.time()
if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = []
if 'uploaded_files' not in st.session_state:
    st.session_state.uploaded_files = None
if 'file_contents' not in st.session_state:
    st.session_state.file_contents = {}

def check_session_timeout():
    """Check if the session has timed out and reset if necessary."""
    current_time = time.time()
    if current_time - st.session_state.last_activity > SESSION_TIMEOUT:
        # Reset session state
        st.session_state.conversation_history = []
        st.session_state.uploaded_files = None
        st.session_state.file_contents = {}
        st.warning("Your session has timed out. Please upload your files again.")
    st.session_state.last_activity = current_time

# Initialize the LLM (Language Learning Model)
@st.cache_resource
def get_llm() -> ChatOpenAI:
    try:
        # Configure OpenAI API using Azure OpenAI
        openai.api_key = os.getenv("API_KEY")
        openai.api_base = os.getenv("ENDPOINT")
        openai.api_type = "azure"
        openai.api_version = os.getenv("OPENAI_API_VERSION")
        
        # OpenAI Settings
        openai_embeddings = OpenAIEmbeddings(
            openai_api_version=os.getenv("OPENAI_API_VERSION"), 
            openai_api_key=os.getenv("API_KEY"),
            openai_api_base=os.getenv("ENDPOINT"), 
            openai_api_type="azure"
        )
        
        llm = ChatOpenAI(
            temperature=0.3, openai_api_key=os.getenv("API_KEY"), 
            openai_api_base=os.getenv("ENDPOINT"), model_name="gpt-35-turbo", engine="Voicetask"
        )
        
        logging.info("LLM initialized successfully.")
        return llm
    except Exception as e:
        logging.error(f"Error initializing LLM: {e}")
        st.error("An error occurred while initializing the language model. Please try again later.")
        return None

llm = get_llm()

# Sidebar configuration for file uploads
with st.sidebar:
    st.subheader("Upload your document")
    uploaded_files = st.sidebar.file_uploader(
        "Choose files", accept_multiple_files=True, type=["pdf", "txt", "pptx"], key="file_uploader"
    )
    
    if uploaded_files:
        check_session_timeout()
        if len(uploaded_files) > 2:
            st.error("You can only upload a maximum of 2 documents.")
            logging.warning("User attempted to upload more than 2 documents.")
        else:
            valid_files = []
            for file in uploaded_files:
                if allowed_files(file.name):
                    num_pages = file_check_num(file)
                    if num_pages > 50:
                        st.error(f"{file.name} exceeds the 50-page limit (has {num_pages} pages).")
                        logging.warning(f"File {file.name} exceeds the page limit.")
                    else:
                        valid_files.append(file)
                else:
                    st.error(f"{file.name} is not a valid file type.")
                    logging.warning(f"Invalid file type: {file.name}")

            if valid_files:
                try:
                    extraction_results = extract_contents_from_doc(valid_files, "temp_dir")
                    st.session_state.uploaded_files = valid_files
                    st.session_state.file_contents = extraction_results
                    st.success(f"{len(valid_files)} file(s) uploaded and processed successfully.")
                    logging.info("File(s) uploaded and processed successfully.")
                except Exception as e:
                    st.error("An error occurred while processing your document. Please try again.")
                    logging.error(f"Error extracting content from document: {e}")

def send_response(message, response=None):
    check_session_timeout()
    dummy_response = "Hello. How are you?"
    response_text = response or dummy_response
    st.session_state.conversation_history.append(('assistant', response_text))
    print(response_text)
    synthesize_speech(text=response_text)

# Chat area and audio input handling
def send_message():
    check_session_timeout()
    prompt = st.session_state.prompt
    st.session_state.conversation_history.append(('user', prompt))
    
    # get response turn it to speech and reply user
    send_response(prompt)

# Display conversation history
for speaker, message in st.session_state.conversation_history:
    with st.chat_message(speaker):
        st.write(message)

# Handle audio input
st.audio_input("Speak your message", key="audio_prompt", on_change=handle_audio_message)
