# extract_pdf.py -- Funciones para extraer texto de PDFs usando OCR (Tesseract o EasyOCR)
# Entrada de la ruta de pdf, salida de texto extraído

import easyocr
import pytesseract
from PIL import Image
from pdf2image import convert_from_path
import requests
import os
import dotenv

TESSERACT_AVAILABLE = True

dotenv.load_dotenv()

# Formar ruta para lectura del PDF
# pdf_path = os.path.join(pdf_folder, pdf_file)

if TESSERACT_AVAILABLE:
    print("[...] Tesseract OCR está disponible")
    lenguaje = 'spa'  # Cambia esto al código de idioma que necesites (por ejemplo, 'en' para inglés)
else:
    print("[...] Tesseract OCR no está disponible, usando EasyOCR") 
    lenguaje = 'es'  # Cambia esto al código de idioma que necesites (por ejemplo, 'en' para inglés)


def extract_pdf(pdf_path, lenguaje='es', use_tesseract=True):
    """
    Extrae texto de PDF usando OCR.
    
    Args:
        pdf_path (str): Ruta al archivo PDF
        lenguaje (str): Código del idioma para OCR
        use_tesseract (bool): Si True, usa Tesseract; si False, usa EasyOCR
        
    Returns:
        str: Texto extraído del PDF
    """    
    # Usar EasyOCR para extraer texto del PDF
    reader = easyocr.Reader([lenguaje])  # Spanish
    images = convert_from_path(pdf_path)
    
    full_text = ""
    for page_num, image in enumerate(images):
        results = reader.readtext(image)
        text = "\n".join([text for (_, text, _) in results])
        full_text += f"\n--- Página {page_num + 1} ---\n{text}"

    # Intentar usar Tesseract si está disponible
    if use_tesseract and TESSERACT_AVAILABLE:
        print("[...] Usando Tesseract OCR")
        for page_num, image in enumerate(images):
            # Tesseract trabaja directamente con imágenes PIL
            text = pytesseract.image_to_string(image, lang=lenguaje)
            full_text += f"\n--- Pagina {page_num + 1} ---\n{text}"
    
    return full_text

