#functions to check files compatibility and don't exceed the 50 page limit
from io import BytesIO
from PyPDF2 import PdfReader
from pptx import Presentation

allowed_files_list = ["pdf", "txt", "pptx"]
def allowed_files(filename): 
    '''
    Returns True if the file type is in the allowed file list
    '''
    return "." in filename and filename.rsplit(".",1)[1].lower() in allowed_files_list

def file_check_num(uploaded_file):
    '''
    Returns the number of pages (for PDFs), slides (for PPTX), or lines (for TXT) in the file
    '''
    file_ext = uploaded_file.name.rsplit(".", 1)[1].lower() #extract the file extension only
    if file_ext == "pdf":
        pdf_bytes = BytesIO(uploaded_file.read())
        pdf_reader = PdfReader(pdf_bytes)
        uploaded_file.seek(0) 
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
    




#using azure document intelligence to extract content from the document 
import logging
import os 
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.core.credentials import AzureKeyCredential

#setting up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

# # Constants for Azure Speech Services
# DI_ENDPOINT = os.getenv("DI_ENDPOINT")
# DOCUMENT_INTELLIGENCE_KEY = os.getenv('SUBSCRIPTION_KEY')

# document_intelligence_client = DocumentIntelligenceClient(
#     endpoint=DI_ENDPOINT,
#     credential=AzureKeyCredential(DOCUMENT_INTELLIGENCE_KEY)
# )

def extract_contents_from_doc(files, temp_dir):
    """
    Azure Document Intelligence
    Args: files(uploaded by the user), temp_dir(to store the extracted contents from the file(s))
    Returns a directory containing a file stored with the document's extracted content
    """
    # Constants for Azure Document Intelligence 
    DI_ENDPOINT = os.getenv("DOCUMENT_INTELLIGENCE_ENDPOINT") #document intelligence endpoint in the .env file
    DOCUMENT_INTELLIGENCE_KEY = os.getenv('DOCUMENT_INTELLIGENCE_SUBSCRIPTION_KEY') #document intelligence subscription key

    document_intelligence_client = DocumentAnalysisClient(
        endpoint=DI_ENDPOINT,
        credential=AzureKeyCredential(DOCUMENT_INTELLIGENCE_KEY)
    )

    os.makedirs(temp_dir, exist_ok=True) #creating the temporary directory
    logger.info(f"Temporary directory '{temp_dir}' is ready.")

    extracted_file_paths = []

    # checks = file_check_num(files)
    # if checks["status_code"] == 200:
    for file in files:
        try:
            # Read file content
            file_content = file.read()
            logger.info(f"Processing file: {file.name}")
                
            extract = document_intelligence_client.begin_analyze_document(
                    "prebuilt-read",  
                    file_content
                )
            result = extract.result()
            logger.info(f"OCR completed for file: {file.name}")

            extracted_content = ""
            for page in result.pages:
                for line in page.lines:
                    extracted_content += line.content + "\n"
                
            #securing the filename and defining a path for the extracted content
            filename = secure_filename(file.name)
            base, ext = os.path.splitext(filename)
            extracted_filename = f"{base}_extracted.{ext}"
            file_path = os.path.join(temp_dir, extracted_filename)

            # Save the extracted content to a text file
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(extracted_content)
            
            logger.info(f"Extracted content saved to: {file_path}")

            extracted_file_paths.append(file_path)

        except Exception as e:
            logger.error(f"Error processing file '{file.name}': {e}")
            continue  # Proceed with the next file

    return extracted_file_paths
    
        