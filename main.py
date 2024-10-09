import streamlit as st
st.set_page_config(page_title="Speak-To-Docs", page_icon="📝", layout="wide", initial_sidebar_state="expanded")

import os

# Langchain components
from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI

# Add OpenAI library
import openai

# Get Configuration Settings
from dotenv import load_dotenv
load_dotenv()

@st.cache_resource
def get_llm() -> ChatOpenAI:
    # Configure OpenAI API using Azure OpenAI
    openai.api_key = os.getenv("API_KEY")
    openai.api_base = os.getenv("ENDPOINT")
    openai.api_type = "azure"  # Necessary for using the OpenAI library with Azure OpenAI
    openai.api_version = os.getenv("OPENAI_API_VERSION")  # Latest / target version of the API

    # Implementation
    from langchain.embeddings import OpenAIEmbeddings

    # OpenAI Settings
    model_deployment = "text-embedding-ada-002"
    # SDK calls this "engine", but naming it "deployment_name" for clarity

    model_name = "text-embedding-ada-002"

    openai_embeddings: OpenAIEmbeddings = OpenAIEmbeddings(
        openai_api_version = os.getenv("OPENAI_API_VERSION"), openai_api_key = os.getenv("API_KEY"),
        openai_api_base = os.getenv("ENDPOINT"), openai_api_type = "azure"
    )

    # LLM - Azure OpenAI
    llm = ChatOpenAI(temperature = 0.3, openai_api_key = os.getenv("API_KEY"), openai_api_base = os.getenv("ENDPOINT"), model_name="gpt-35-turbo", engine="Voicetask")
    return llm

llm = get_llm()

#sidebar configuration
#import the file check functions
from src.rag_functions import *

if 'uploaded_files' not in st.session_state:
    st.session_state.uploaded_files = None

with st.sidebar:
    st.subheader("Upload your document")
    st.session_state.uploaded_files = st.sidebar.file_uploader("Choose files", 
                                              accept_multiple_files=True, type=["pdf", "txt", "pptx"],
                                                key="initial")
    if st.session_state.uploaded_files:
        if len(st.session_state.uploaded_files) > 2:
            st.error("You can only upload a maximum of 2 documents.")
            st.session_state.uploaded_files = None
        else:
            #set a valid upload to True
            valid_file = True
            for file in st.session_state.uploaded_files:
                if allowed_files(file.name):
                  num_pages = file_check_num(file)
                  if num_pages > 50:
                      st.error(f"{file.name} exceeds the 50-page limit (has {num_pages} pages).")
                      valid_file = False
                      break
                else:
                      st.error(f"{file.name} is not a valid file type.")
                      valid_file = False
                      break

            if valid_file:
                st.success(f"{len(st.session_state.uploaded_files)} file(s) uploaded successfully.")
    else:
        st.session_state.uploaded_files = None
                  
              
    

#chat area
message = st.container()
if prompt:=st.chat_input("Enter your query"):
    message.chat_message("user").write(prompt)



    
