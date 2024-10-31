import streamlit as st
import os
import logging
from dotenv import load_dotenv
from src.speech_io import transcribe_audio, synthesize_speech
from src.rag_functions import (allowed_files, file_check_num, 
                               extract_contents_from_doc, chunk_document, logger)
from langchain.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import DocArrayInMemorySearch
from langchain.chains.retrieval_qa.base import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.schema import Document
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

#function to embed the chunks created on docs and initializing a vector store
def create_vector_store(extracted_file_paths):
    """
    Embeds the documents and initializes a DocArrayInMemorySearch vector store.

    Args:
        extracted_file_path: A path containing the contents extracted from the documents uploaded

    Returns:
        DocArrayInMemorySearch: An initialized vector store with embedded documents.
    """
    try:
        #OpenAI Embedding settings
        openai_embeddings = OpenAIEmbeddings(
                openai_api_version=os.getenv("OPENAI_API_VERSION"), 
                openai_api_key=os.getenv("API_KEY"),
                openai_api_base=os.getenv("ENDPOINT"), 
                openai_api_type="azure",
                deployment="text-embedding-ada-002"
            )
        logger.info("OpenAI Embeddings initialized successfully.")
        docs = []
        for file_path in extracted_file_paths:
            try:
                with open(file_path, "r", encoding="utf-8") as file:
                    text = file.read()
                chunks = chunk_document(text)
                docs.extend([Document(page_content=chunk) for chunk in chunks])
                logger.info(f"Document {file_path} chunked into {len(chunks)} chunks.")
            except Exception as e:
                logger.error(f"Error reading or chunking file '{file_path}': {e}")
                continue

        #initializing the vector store
        vector_store = DocArrayInMemorySearch.from_documents(docs, openai_embeddings)
        logger.info("DocArrayInMemorySearch vector store initialized successfully.")

        return vector_store
    
    except Exception as e:
        logger.exception(f"An error occurred while initializing the vector store: {e}")

def query_response(query:str, vector_store, llm):
    """
    Generates a response to the user's query using the vector store and language model.
    Utilizes LangChain's retrieval library: RetrievalQA.

    Args:
        query (str): The user's input query.
        vector_store (DocArrayInMemorySearch): The initialized vector store.
        llm (BaseLLM): The language model to generate responses.
        choice_k (int, optional): Number of chunks to retrieve for similarity search. Default is 3.

    Returns:
        str: The generated response, or a message if an error occurred.
    """
    try:
        #prompting for the llm 
        prompt_template = """Use the following excerpts to answer a query. If you can't find the answer from the provided document,
            don't try to make up an answer. Just say "I can't find the answer from the provided document. You can try to upload a more detailed document."

    Context: {context}

    Question: {question}

    Helpful Answer:
    """
        # Check if response for this query already exists in session_state cache
        if "query_history" not in st.session_state:
            st.session_state["query_history"] = {}

        # If query is cached, return the cached response
        if query in st.session_state["query_history"]:
            return st.session_state["query_history"][query]
        
        prompt = PromptTemplate(
        template=prompt_template, input_variables=["context", "question"]
        )

        retrieval_chain = RetrievalQA.from_chain_type(
            llm = llm,
            chain_type= "stuff",
            retriever = vector_store.as_retriever(search_type ="similarity",search_kwargs={"k": 3}),
            #return_source_documents=True,
            chain_type_kwargs={"prompt": prompt}
        )
        
        response = retrieval_chain.invoke({"query":query})
        # Cache the response in session_state to optimize future queries
        st.session_state["query_history"][query] = response

        return response["result"]

    except Exception as e:
        logger.error(f"Error occurred in generating response:{e}")
        return "Sorry, I couldn't process your request at the moment."


# Sidebar configuration for file uploads
if 'uploaded_files' not in st.session_state:
    st.session_state.uploaded_files = None
    st.session_state['prev_uploaded_files'] = []

with st.sidebar:
    st.subheader("Upload your document")
    uploaded_files = st.sidebar.file_uploader(
        "Choose files", accept_multiple_files=True, type=["pdf", "txt", "pptx"], key="initial"
    )
    
    # Check for changes in the uploaded files
    if uploaded_files:
        uploaded_file_names = [file.name for file in uploaded_files]
        prev_file_names = [file.name for file in st.session_state['prev_uploaded_files']]
        
        # Check if there's any difference between the current and previous file names
        if uploaded_file_names != prev_file_names:
            st.session_state.uploaded_files = uploaded_files
            st.session_state['prev_uploaded_files'] = uploaded_files

            if len(uploaded_files) > 2:
                st.error("You can only upload a maximum of 2 documents.")
                logging.warning("User attempted to upload more than 2 documents.")
                st.session_state.uploaded_files = None
            else:
                valid_files = []
                valid_file = True
                for file in uploaded_files:
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
                            st.success(f"{len(uploaded_files)} file(s) uploaded and processed successfully.")
                            logging.info("File(s) uploaded and processed successfully.")
                    except Exception as e:
                        st.error("An error occurred while processing your document. Please try again.")
                        logging.error(f"Error extracting content from document: {e}")
    else:
        st.session_state.uploaded_files = None
        st.session_state['prev_uploaded_files'] = []
        
    st.subheader("Speech output responses")
    if 'speech_outputs' in st.session_state:
        for speech_output in st.session_state.speech_outputs:
            st.audio(os.path.join('speech_outputs', speech_output), format="audio/wav", start_time=0)

def send_response(query, response=None):
    # dummy_response = "Hello. How are you?"
    # st.session_state.messages.append(('assistant', response or dummy_response))
    """
    Sends a response to the user by querying the RAG chain and converting it to speech.
    """
    if response is None:
        # Use the RAG query function to get a response based on user input
        response = query_response(query, vector_store=vector_store, llm=llm)
    
    # Append the generated response to the chat history
    st.session_state.messages.append(('assistant', response))
    # TODO: make async ??
    # generate unique file name
    output_file = uuid.uuid4().hex + ".wav"
    synthesize_speech(output_file=output_file, text=response)
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
            send_response(speech_text)
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
