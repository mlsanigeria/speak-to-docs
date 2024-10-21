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
import uuid

# Set up page configuration
st.set_page_config(page_title="Speak-To-Docs", page_icon="📝", layout="wide", initial_sidebar_state="expanded")

# Configure logging
logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s:%(levelname)s:%(message)s')

# Load environment variables
load_dotenv()

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
if 'uploaded_files' not in st.session_state:
    st.session_state.uploaded_files = None

with st.sidebar:
    st.subheader("Upload your document")
    st.session_state.uploaded_files = st.sidebar.file_uploader(
        "Choose files", accept_multiple_files=True, type=["pdf", "txt", "pptx"], key="initial"
    )
    
    if st.session_state.uploaded_files:
        if len(st.session_state.uploaded_files) > 2:
            st.error("You can only upload a maximum of 2 documents.")
            logging.warning("User attempted to upload more than 2 documents.")
            st.session_state.uploaded_files = None
        else:
            valid_files = []
            valid_file = True
            for file in st.session_state.uploaded_files:
                if allowed_files(file.name):
                    num_pages = file_check_num(file)
                    if num_pages > 50:
                        st.error(f"{file.name} exceeds the 50-page limit (has {num_pages} pages).")
                        logging.warning(f"File {file.name} exceeds the page limit.")
                        valid_file = False
                        break
                    else:
                        valid_files.append(file)
                else:
                    st.error(f"{file.name} is not a valid file type.")
                    logging.warning(f"Invalid file type: {file.name}")
                    valid_file = False
                    break

            if valid_file and valid_files:
                try:
                    extraction_results = extract_contents_from_doc(valid_files, "temp_dir")
                    st.success(f"{len(st.session_state.uploaded_files)} file(s) uploaded and processed successfully.")
                    logging.info("File(s) uploaded and processed successfully.")
                except Exception as e:
                    st.error("An error occurred while processing your document. Please try again.")
                    logging.error(f"Error extracting content from document: {e}")
    else:
        st.session_state.uploaded_files = None
        
    st.subheader("Speech output responses")
    if 'speech_outputs' in st.session_state:
        for speech_output in st.session_state.speech_outputs:
            st.audio(os.path.join('speech_outputs', speech_output), format="audio/wav", start_time=0)

def send_response(message, response=None):
    dummy_response = "Hello. How are you?"
    st.session_state.messages.append(('assistant', response or dummy_response))
    
    # TODO: make async ??
    # generate unique file name
    output_file = uuid.uuid4().hex + ".wav"
    synthesize_speech(output_file=output_file, text=response or dummy_response)
    st.session_state.speech_outputs.append(output_file)
    

# Chat area and audio input handling
def send_message():
    prompt = st.session_state.prompt
    st.session_state.messages.append(('user', prompt))
    
    # get response turn it to speech and reply user
    send_response(prompt)


if 'messages' not in st.session_state:
    st.session_state.messages = []
    
if 'speech_outputs' not in st.session_state:
    st.session_state.speech_outputs = []

message = st.container()

# Handle text input from user
# if prompt := st.chat_input("Enter your query"):
#     message.chat_message("user").write(prompt)

def handle_audio_message():
    audio_value = st.session_state.audio_prompt
    try:
        with open("audio.wav", "wb") as f:
            f.write(audio_value.getbuffer())
        
        speech_text = transcribe_audio("audio.wav")
        if speech_text:
            st.session_state.messages.append(("user", speech_text))
            send_response(speech_text, "You have a great voice")
            logging.info("Audio transcribed successfully.")
        else:
            # st.session_state.messages.append(("assistant", ))
            send_response(speech_text, "Sorry, I couldn't transcribe your audio. Please try again.")
            logging.warning("Audio transcription failed.")
    except Exception as e:
        st.error("An error occurred while processing the audio. Please try again.")
        logging.error(f"Error processing audio input: {e}")  


# Input area for user queries
st.chat_input("Enter your query", key='prompt', on_submit=send_message)

# Display chat messages

# with message:
for role, text in st.session_state.messages:
    st.chat_message(role).write(text)
    

# Handle audio input from user
audio_value = st.experimental_audio_input("Record a voice message", key="audio_prompt", on_change=handle_audio_message)
