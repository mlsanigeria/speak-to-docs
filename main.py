import streamlit as st
import os
import logging
from dotenv import load_dotenv
from src.speech_io import transcribe_audio, synthesize_speech
from src.rag_functions import (allowed_files, file_check_num, 
                               extract_contents_from_doc, create_vector_store, logger)
from langchain.chains.retrieval import create_retrieval_chain
from langchain.chains.history_aware_retriever import create_history_aware_retriever
from langchain.chat_models import ChatOpenAI
from langchain.embeddings import OpenAIEmbeddings
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import PromptTemplate
import openai

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
        
        # # OpenAI Settings
        # openai_embeddings = OpenAIEmbeddings(
        #     openai_api_version=os.getenv("OPENAI_API_VERSION"), 
        #     openai_api_key=os.getenv("API_KEY"),
        #     openai_api_base=os.getenv("ENDPOINT"), 
        #     openai_api_type="azure"
        # )
        
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

    
def query_response(query, vector_store):
    """
    Generates a response to the user's query using the vector store and the language model.
    Uses Langchains retrieval library

    Args:
        query (str): The user's input query.
        vector_store (DocArrayInMemorySearch): The initialized vector store

    Returns:
        str: The generated response.
    """
    try:
        llm = get_llm()
        #prompting for the llm 
        prompt_template = """Use the following excerpts to answer a query. If you can't find the answer from the provided document,
            don't try to make up an answer. Just say "I can't find the answer from the provided document but you may want to check the following links".

    Context: {context}

    Question: {question}

    Helpful Answer:
    """
        qa_prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
        # Create history-aware retriever
        history_aware_retriever = create_history_aware_retriever(
            llm,
            vector_store.as_retriever(search_type="similarity",
                                    search_kwargs={"k": 3},),
            qa_prompt,)
        #initializing  a question answer chain
        question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)

        #query retrieval chain
        chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)

        #retrieve answer
        response = chain.invoke({"question": query})
        logger.info("Response successfully generated")
        return response["answer"]

    except Exception as e:
        logger.error(f"Error occurred in generating response:{e}")
        return "Sorry, I couldn't process your request at the moment."


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
                    vector_store = create_vector_store(extraction_results)
                    if vector_store:
                        st.session_state['vector_store'] = vector_store
                        st.success(f"{len(st.session_state.uploaded_files)} file(s) uploaded and processed successfully.")
                        logging.info("File(s) uploaded and processed successfully.")
                except Exception as e:
                    st.error("An error occurred while processing your document. Please try again.")
                    logging.error(f"Error extracting content from document: {e}")
    else:
        st.session_state.uploaded_files = None


def send_response(message, response=None):
    # dummy_response = "Hello. How are you?"
    # st.session_state.messages.append(('assistant', response or dummy_response))
    # TODO: make async ??
    vector_store = st.session_state['vector_store']

    # Get the response from query_response
    answer = query_response(message, vector_store)

    # Append the assistant's response to messages
    st.session_state.messages.append(('assistant', answer))

    print(answer)
    synthesize_speech(text=answer)
    

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
            #send_response(speech_text, "You have a great voice")
            send_response(speech_text)
            logging.info("Audio transcribed and response generated successfully.")
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
