from io import BytesIO
from PyPDF2 import PdfReader
from pptx import Presentation
import logging
import os
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import DocArrayInMemorySearch
from langchain.schema import Document


# Setting up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

# Allowed file types
allowed_files_list = ["pdf", "txt", "pptx"]

def allowed_files(filename):
    '''
    Returns True if the file type is in the allowed file list
    '''
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed_files_list

def file_check_num(uploaded_file):
    '''
    Returns the number of pages (for PDFs), slides (for PPTX), or lines (for TXT) in the file
    '''
    file_ext = uploaded_file.name.rsplit(".", 1)[1].lower()  # Extract the file extension
    try:
        if file_ext == "pdf":
            pdf_bytes = BytesIO(uploaded_file.read())
            pdf_reader = PdfReader(pdf_bytes)
            uploaded_file.seek(0)  # Reset file pointer after reading
            return len(pdf_reader.pages)
        
        elif file_ext == "pptx":
            pptx_bytes = BytesIO(uploaded_file.read())
            pptx = Presentation(pptx_bytes)
            uploaded_file.seek(0)
            return len(pptx.slides)
        
        elif file_ext == "txt":
            num = len(uploaded_file.read().decode("utf-8").splitlines())
            uploaded_file.seek(0)
            return num
        else:
            logger.error(f"Unsupported file extension: {file_ext}")
            return -1
    except Exception as e:
        logger.error(f"Error checking file '{uploaded_file.name}': {e}")
        return -1



def chunk_document(text, chunk_size=1000, chunk_overlap=200):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
    )
    chunks = text_splitter.split_text(text)
    return chunks

def extract_contents_from_doc(files, temp_dir):
    """
    Azure Document Intelligence
    Args: 
        files (uploaded by the user): List of uploaded files to process.
        temp_dir (str): Directory path to store the extracted contents.
    
    Returns: 
        List of file paths where the extracted content is stored.
    """
    # Constants for Azure Document Intelligence
    DI_ENDPOINT = os.getenv("DOCUMENT_INTELLIGENCE_ENDPOINT")
    DOCUMENT_INTELLIGENCE_KEY = os.getenv('DOCUMENT_INTELLIGENCE_SUBSCRIPTION_KEY')

    if not DI_ENDPOINT or not DOCUMENT_INTELLIGENCE_KEY:
        logger.error("Azure Document Intelligence credentials are missing.")
        return []

    document_intelligence_client = DocumentAnalysisClient(
        endpoint=DI_ENDPOINT,
        credential=AzureKeyCredential(DOCUMENT_INTELLIGENCE_KEY)
    )

    # Ensure the temporary directory exists
    os.makedirs(temp_dir, exist_ok=True)
    logger.info(f"Temporary directory '{temp_dir}' is ready.")

    extracted_file_paths = []

    for file in files:
        try:
            # Read file content
            file_content = file.read()
            logger.info(f"Processing file: {file.name}")
                
            # Perform content extraction using Azure's "prebuilt-read" model
            extract = document_intelligence_client.begin_analyze_document("prebuilt-read", file_content)
            result = extract.result()
            logger.info(f"OCR completed for file: {file.name}")

            # Extract content from each page
            extracted_content = ""
            for page in result.pages:
                for line in page.lines:
                    extracted_content += line.content + "\n"
            
            # Secure the filename and define a path for saving extracted content
            filename = secure_filename(file.name)
            base, ext = os.path.splitext(filename)
            extracted_filename = f"{base}_extracted.txt"  # Save as .txt for easier reading
            file_path = os.path.join(temp_dir, extracted_filename)

            # Save the extracted content to a file
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(extracted_content)
            
            logger.info(f"Extracted content saved to: {file_path}")
            extracted_file_paths.append(file_path)

        except Exception as e:
            logger.error(f"Error processing file '{file.name}': {e}")
            continue  # Proceed with the next file in case of an error

    return extracted_file_paths

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
