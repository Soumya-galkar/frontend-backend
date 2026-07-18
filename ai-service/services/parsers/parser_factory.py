import os

from services.pdf_parser import extract_text_from_pdf
from services.parsers.docx_parser import extract_text_from_docx
from services.parsers.image_parser import extract_text_from_image
from services.parsers.excel_parser import extract_text_from_excel
from services.parsers.email_parser import extract_text_from_email
from services.parsers.pid_parser import parse_pid


def parse_document(file_path):

    extension = os.path.splitext(file_path)[1].lower()

    if extension == ".pdf":
        return extract_text_from_pdf(file_path)

    elif extension == ".docx":
        return extract_text_from_docx(file_path)

    elif extension in [".png", ".jpg", ".jpeg", ".bmp", ".tiff"]:
        return extract_text_from_image(file_path)
    
    elif extension in [".xlsx", ".xls"]:
        return extract_text_from_excel(file_path)
    
    elif extension == ".eml":
        return  extract_text_from_email(file_path)
    
    elif extension in [".png", ".jpg", ".jpeg", ".tif", ".tiff"]:
        return parse_pid(file_path)

    else:
        raise Exception(f"Unsupported file format: {extension}")