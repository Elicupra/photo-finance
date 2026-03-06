import easyocr
from pdf2image import convert_from_path
import requests
import os
import dotenv
import numpy as np

#dotenv.load_dotenv()
pdf_file = "Naturgy_01_25.pdf"
pdf_folder = "container_pdf"
pdf_path = os.path.join(pdf_folder, pdf_file)

def extract_pdf(pdf_path, lenguaje='es'):
    """Extrae texto con EasyOCR"""
    reader = easyocr.Reader([lenguaje])  # Spanish
    images = convert_from_path(pdf_path)
    
    full_text = ""
    for page_num, image in enumerate(images):
        results = reader.readtext(np.array(image))
        text = "\n".join([text for (_, text, _) in results])
        full_text += f"\n--- Página {page_num + 1} ---\n{text}"
    
    return print(full_text)

if __name__ == "__main__":
    print(f"Extracting text from PDF: {pdf_path}")
    extract_pdf(pdf_path)