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

#sidebar configuration
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
            # 200MB limit
            limit = 200
            for file in st.session_state.uploaded_files:
                # convert bytes to MB
                size_mb = (file.size / (1024 * 1024))
                if size_mb > limit:
                    st.error(f"{file.name} is too large ({size_mb:.2f} MB). Please upload a file less than {limit} MB.")
                    st.session_state.uploaded_files = None
                    break
                
        if st.session_state.uploaded_files:
            st.success(f"{len(st.session_state.uploaded_files)} file(s) uploaded.")

#chat area
message = st.container()
if prompt:=st.chat_input("Enter your query"):
    message.chat_message("user").write(prompt)

    
