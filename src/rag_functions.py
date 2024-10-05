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
        return len(pdf_reader.pages)
    
    elif file_ext == "pptx":
        pptx_bytes = BytesIO(uploaded_file.read())
        pptx = Presentation(pptx_bytes)
        return len(pptx.slides)
    
    elif file_ext == "txt":
        return len(uploaded_file.read().decode("utf-8").splitlines())
