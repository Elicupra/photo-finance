# extract_pdf.py -- Funciones para extraer texto de PDFs usando OCR (Tesseract o EasyOCR)
# Entrada de la ruta de pdf, salida de texto extraído
# basado en español y facturas del modelo español

import easyocr
import pytesseract
import numpy as np
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
    images = convert_from_path(pdf_path)
    full_text = ""
    
    # Priorizar Tesseract si está disponible y se solicita
    if use_tesseract and TESSERACT_AVAILABLE:
        print("[...] Usando Tesseract OCR")
        lenguaje_tess = 'spa' if lenguaje == 'es' else lenguaje
        for page_num, image in enumerate(images):
            # Configurar pytesseract para GPU si es posible
            custom_config = r'--oem 3 --psm 6' # OEM 3 = Default, PSM 6 = Assume a single uniform block of text 
            
            text = pytesseract.image_to_string(image, lang=lenguaje_tess, config=custom_config)
            full_text += f"\n--- Página {page_num + 1} ---\n{text}"
    else:
        # Usar EasyOCR como fallback
        print("[...] Usando EasyOCR")
        reader = easyocr.Reader([lenguaje])
        for page_num, image in enumerate(images):
            # Convertir imagen PIL a numpy array para EasyOCR
            image_array = np.array(image)
            results = reader.readtext(image_array)
            text = "\n".join([text for (_, text, _) in results])
            full_text += f"\n--- Página {page_num + 1} ---\n{text}"
    
    return full_text

