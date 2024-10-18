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
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS

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
    st.subheader("Upload your documents")
    st.session_state.uploaded_files = st.sidebar.file_uploader(
        "Choose up to 2 files", accept_multiple_files=True, type=["pdf", "txt", "pptx"], key="initial"
    )
    
    if st.session_state.uploaded_files:
        if len(st.session_state.uploaded_files) > 2:
            st.error("You can only upload a maximum of 2 documents.")
            st.session_state.uploaded_files = None
        else:
            valid_files = []
            for file in st.session_state.uploaded_files:
                if allowed_files(file.name):
                    num_pages = file_check_num(file)
                    if num_pages > 50:
                        st.error(f"{file.name} exceeds the 50-page limit (has {num_pages} pages).")
                    else:
                        valid_files.append(file)
                else:
                    st.error(f"{file.name} is not a valid file type.")
            
            if valid_files:
                st.success(f"{len(valid_files)} file(s) uploaded successfully.")
                # Process the valid files
                try:
                    extracted_contents = extract_contents_from_doc(valid_files, "temp_dir")
                    st.session_state.extracted_contents = extracted_contents
                    st.success("Files processed successfully.")
                except Exception as e:
                    st.error(f"An error occurred while processing your documents: {str(e)}")
            else:
                st.session_state.uploaded_files = None
    else:
        st.session_state.uploaded_files = None


def send_response(message, response=None):
    if 'rag_chain' in st.session_state:
        rag_response = st.session_state.rag_chain.run(message)
        st.session_state.messages.append(('assistant', rag_response))
        synthesize_speech(text=rag_response)
    else:
        dummy_response = "Please upload documents to use the RAG system."
        st.session_state.messages.append(('assistant', dummy_response))
        synthesize_speech(text=dummy_response)
    

# Chat area and audio input handling
def send_message():
    prompt = st.session_state.prompt
    st.session_state.messages.append(('user', prompt))
    
    # get response turn it to speech and reply user
    send_response(prompt)


if 'messages' not in st.session_state:
    st.session_state.messages = []

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

def create_vectorstore(extracted_contents):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    texts = []
    for content in extracted_contents:
        with open(content, 'r') as f:
            text = f.read()
            texts.extend(text_splitter.split_text(text))
    
    embeddings = OpenAIEmbeddings()
    vectorstore = FAISS.from_texts(texts, embeddings)
    return vectorstore

def setup_rag(vectorstore, llm):
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
    rag_chain = RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", retriever=retriever)
    return rag_chain

# Add this after processing the valid files
if 'extracted_contents' in st.session_state:
    vectorstore = create_vectorstore(st.session_state.extracted_contents)
    st.session_state.rag_chain = setup_rag(vectorstore, llm)
