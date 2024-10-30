import streamlit as st
import os
import logging
from dotenv import load_dotenv
from src.speech_io import transcribe_audio, synthesize_speech
from src.rag_functions import (allowed_files, file_check_num, 
                               extract_contents_from_doc, chunk_document, logger)
from langchain.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import DocArrayInMemorySearch
from langchain.schema import Document
from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.memory import ConversationBufferMemory
import openai
import uuid

# Set up page configuration
st.set_page_config(page_title="Speak-To-Docs", page_icon="📝", layout="wide")

# Configure logging
logging.basicConfig(filename='app.log', level=logging.INFO, 
                   format='%(asctime)s:%(levelname)s:%(message)s')

# Load environment variables
load_dotenv()

# Initialize the RAG chain
@st.cache_resource
def initialize_rag_chain(vector_store):
    """
    Initialize the RAG chain with conversation memory and caching
    """
    try:
        # Initialize LLM with Azure OpenAI
        llm = ChatOpenAI(
            temperature=0.3,
            openai_api_key=os.getenv("API_KEY"),
            openai_api_base=os.getenv("ENDPOINT"),
            model_name="gpt-35-turbo",
            engine="Voicetask"
        )
        
        # Initialize conversation memory
        memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True,
            output_key="answer"
        )
        
        # Create RAG chain with memory
        rag_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=vector_store.as_retriever(
                search_type="similarity",
                search_kwargs={"k": 3}
            ),
            memory=memory,
            return_source_documents=True,
            verbose=True
        )
        
        logging.info("RAG chain initialized successfully with conversation memory.")
        return rag_chain
    except Exception as e:
        logging.error(f"Error initializing RAG chain: {e}")
        st.error("Failed to initialize the RAG system. Please try again.")
        return None

def process_query(query, rag_chain):
    """
    Process user query through the RAG chain with conversation history
    """
    try:
        # Initialize session state for chat history if not exists
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []
        
        # Get response from RAG chain
        response = rag_chain({
            "query": query,
            "chat_history": st.session_state.chat_history
        })
        
        # Extract answer and sources
        answer = response['result']
        sources = response.get('source_documents', [])
        
        # Update chat history in session state
        st.session_state.chat_history.append({
            "query": query,
            "response": answer,
            "sources": [doc.page_content for doc in sources]
        })
        
        # Cache the response in session state
        if 'response_cache' not in st.session_state:
            st.session_state.response_cache = {}
        st.session_state.response_cache[query] = {
            "answer": answer,
            "sources": sources
        }
        
        return answer, sources
    except Exception as e:
        logging.error(f"Error processing query: {e}")
        return "I apologize, but I encountered an error processing your query.", []
        return answer, sources
    except Exception as e:
        logging.error(f"Error processing query: {e}")
        return "I apologize, but I encountered an error processing your query.", []

def send_response(message, rag_chain):
    # Process query through RAG chain
    response, sources = process_query(message, rag_chain)
    
    # Add to message history
    st.session_state.messages.append(('user', message))
    st.session_state.messages.append(('assistant', response))
    
    # Generate speech output
    output_file = uuid.uuid4().hex + ".wav"
    synthesize_speech(output_file=output_file, text=response)
    st.session_state.speech_outputs.append(output_file)

def get_conversation_context():
    """
    Get formatted conversation context from session state
    """
    if 'chat_history' not in st.session_state:
        return []
    
    context = []
    for entry in st.session_state.chat_history[-5:]:  # Get last 5 conversations
        context.append({
            "role": "user",
            "content": entry["query"]
        })
        context.append({
            "role": "assistant",
            "content": entry["response"]
        })
    return context