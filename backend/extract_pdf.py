import easyocr
from pdf2image import convert_from_path
import requests
import os
import dotenv


dotenv.load_dotenv()

def extract_pdf(pdf_path, lenguaje='es'):
    """Extrae texto con EasyOCR"""
    reader = easyocr.Reader([lenguaje])  # Spanish
    images = convert_from_path(pdf_path)
    
    full_text = ""
    for page_num, image in enumerate(images):
        results = reader.readtext(image)
        text = "\n".join([text for (_, text, _) in results])
        full_text += f"\n--- Página {page_num + 1} ---\n{text}"
    
    return full_text

