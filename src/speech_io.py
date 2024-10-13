from io import BytesIO
from PyPDF2 import PdfReader
from pptx import Presentation
import logging
import os
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
import json

# Setting up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

# Allowed file types
allowed_files_list = ["pdf", "txt", "pptx"]

# Conversation history cache (in-memory)
conversation_history = {}

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

def update_conversation_history(user_id, message):
    """
    Update the conversation history for a user.

    Args:
        user_id (str): The unique identifier of the user.
        message (str): The latest message or query from the user.

    This function stores the conversation history for each user in memory.
    For scalability, it can be extended to use a database.
    """
    if user_id not in conversation_history:
        conversation_history[user_id] = []

    # Limit history to the last 10 messages to avoid performance issues
    if len(conversation_history[user_id]) >= 10:
        conversation_history[user_id].pop(0)  # Remove the oldest message

    # Add the new message to the user's history
    conversation_history[user_id].append(message)
    logger.info(f"Updated conversation history for user {user_id}: {conversation_history[user_id]}")

def get_conversation_context(user_id):
    """
    Retrieve the conversation history for a user.

    Args:
        user_id (str): The unique identifier of the user.

    Returns:
        str: The concatenated history of the user's conversation.
    """
    return " ".join(conversation_history.get(user_id, []))

def generate_answer(user_id, query):
    """
    Generate an answer using the conversation history-aware RAG system.

    Args:
        user_id (str): The unique identifier of the user.
        query (str): The user's latest query.

    Returns:
        str: The generated answer, considering the conversation context.
    """
    # Update the conversation history with the latest query
    update_conversation_history(user_id, query)

    # Get the full conversation context
    conversation_context = get_conversation_context(user_id)

    # Incorporate the context into the RAG process (pseudo-code)
    # This part would typically involve using the context with the model or RAG system.
    # For example:
    # answer = rag_model.generate(query=query, context=conversation_context)
    
    # For now, we mock this process:
    answer = f"Based on the context: '{conversation_context}', here is the answer to '{query}'."

    logger.info(f"Generated answer for user {user_id}: {answer}")
    return answer

# Mock function for processing a user query
def process_user_query(user_id, query):
    """
    Process a user query, using conversation history to enhance the response.

    Args:
        user_id (str): The unique identifier of the user.
        query (str): The user's query.

    Returns:
        str: The RAG-generated answer to the query.
    """
    logger.info(f"Processing query for user {user_id}: {query}")
    
    # Generate an answer using the conversation-aware RAG system
    answer = generate_answer(user_id, query)
    
    return answer
