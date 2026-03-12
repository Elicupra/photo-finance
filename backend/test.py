import easyocr
from pdf2image import convert_from_path
import requests
import os
import dotenv
import numpy as np
import re
import json
import sys
from typing import Dict, Any, List, Optional

# Intentar usar Tesseract si está disponible
try:
    import pytesseract
    from PIL import Image
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False

# Force UTF-8 output on Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

#dotenv.load_dotenv()
pdf_file = "Naturgy_01_26.pdf"
pdf_folder = "container_pdf"
pdf_path = os.path.join(pdf_folder, pdf_file)
 # Cambia esto al código de idioma que necesites (por ejemplo, 'en' para inglés)

def extract_pdf(pdf_path, lenguaje='spa', use_tesseract=True):
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
    
    if use_tesseract and TESSERACT_AVAILABLE:
        print("[...] Usando Tesseract OCR")
        for page_num, image in enumerate(images):
            # Tesseract trabaja directamente con imágenes PIL
            text = pytesseract.image_to_string(image, lang=lenguaje)
            full_text += f"\n--- Pagina {page_num + 1} ---\n{text}"
    else:
        print("[...] Usando EasyOCR")
        reader = easyocr.Reader([lenguaje])
        for page_num, image in enumerate(images):
            results = reader.readtext(np.array(image))
            text = "\n".join([text for (_, text, _) in results])
            full_text += f"\n--- Pagina {page_num + 1} ---\n{text}"
    
    return full_text

def parse_invoice_debt(text: str):
    """
    Procesa el texto extraído para identificar conceptos e importes.
    """
    match = re.search(
        r'TOTAL\s*A\s*PAGAR\s*:?\s*([0-9]{1,4}(?:[.,]\s?[0-9]{2})?)\s*€?',
        text,
        re.IGNORECASE
    )
    if match:
        return float(match.group(1).replace(' ', '').replace(',', '.'))

    return None

def parse_invoice_debt_date(text: str):
    """
    Procesa el texto extraído para identificar la fecha de vencimiento.
    """
    # Lista match_vencimiento con varias expresiones regulares para diferentes formatos de fecha de vencimiento
    patrones = [
        r'FECHA\s*DE\s*VENCIMIENTO\s*:?\s*([0-9]{1,2}\s*/\s*[0-9]{1,2}\s*/\s*[0-9]{2,4})',
        r'FECHA\s*ESTIMADA\s*DE\s*CARGO\s*:?\s*([0-9]{1,2}\s*/\s*[0-9]{1,2}\s*/\s*[0-9]{2,4})',
    ]

    for patron in patrones:
        match = re.search(patron, text, re.IGNORECASE)
        if match:
            return re.sub(r'\s+', '', match.group(1))

    return None

def parse_invoice_subject(text: str):
    """
    Procesa el texto extraído para identificar el asunto o concepto de la factura.
    """
    patrones = [
        r'ASUNTO\s*:?\s*(?:\r?\n\s*)?([^\r\n]+)',
        r'CONCEPTO\s*:?\s*(?:\r?\n\s*)?([^\r\n]+)',
        r'DESCRIPCIÓN\s*:?\s*(?:\r?\n\s*)?([^\r\n]+)',
        r'DETALLE\s*:?\s*(?:\r?\n\s*)?([^\r\n]+)',
        r'CONCEPTO\s*DE\s*LA\s*FACTURA\s*:?\s*(?:\r?\n\s*)?([^\r\n]+)',
        r'PRODUCTO\s*O\s*SERVICIO\s*:?\s*(?:\r?\n\s*)?([^\r\n]+)'
    ]
    for patron in patrones:
        match = re.search(patron, text, re.IGNORECASE)
        if match:
            return match.group(1).strip()

    return None

def find_concepts_keys(text: str):
    """
    Busca palabras clave para identificar el servicio o producto
    
    Args:
        text (str): Texto extraído del PDF
        
    Returns:
        concepto: str: Concepto o servicio identificado
    """
    patrones = [
            r'luz',
            r'electricidad',
        r'Gas\s*Natural',
        r'Agua\s*Potable',
        r'Internet\s*o\s*Fibra\s*Óptica',
        r'Fibra',
        r'Teléfono\s*Fijo\s*o\s*Móvil',
        r'Calefacción\s*o\s*Climatización',
        r'Gasoil\s*o\s*Combustible\s*o\s*Gasóleo\s*o\s*Gasolina\s*o\s*Diesel',
        r'Supermercado\s*o\s*Alimentación\s*o\s*Hipermercado',
        r'Centro\s*Comercial\s*o\s*Tiendas\s*o\s*Retail',
        r'Ropa\s*o\s*Textil',
        r'Entretenimiento\s*o\s*Streaming\s*o\s*Ocio',
        r'Electrodomésticos\s*o\s*Tecnología',
        r'Automóvil\s*o\s*Transporte',
        r'Salud\s*o\s*Farmacia',
        r'Gastos\s*Financieros\s*o\s*Bancarios',
        r'Bazar\s*o\s*Hogar\s*o\s*Decoración',
        r'Viajes\s*o\s*Turismo\s*o\s*Agencia\s*de\s*Viajes',
        r'Gastos\s*Profesionales\s*o\s*Servicios\s*Profesionales',
        r'Gastos\s*de\s*Educación\s*o\s*Formación\s*o\s*Cursos',
        r'Gastos\s*de\s*Salud\s*o\s*Clínicas\s*o\s*Hospitales',
        r'Gastos\s*de\s*Entretenimiento\s*o\s*Cine\s*o\s*Conciertos\s*o\s*Eventos'
    ]

    for patron in patrones:
        claves = re.search(patron, text, re.IGNORECASE)
        if claves:
            return claves.group(0).strip()

    return None

if __name__ == "__main__":
    
    print(f"Procesando: {pdf_file}")
    print(f"Archivo: {pdf_path}")
    print(f"{'─' * 80}")
    print("[...] Extrayendo texto...")
    texto = extract_pdf(pdf_path, lenguaje='spa', use_tesseract=True)
    print(f"{'─' * 80}")
    print("[...] Texto extraído:")
    print(texto)
    print("[...] Procesando conceptos...")
    factura = parse_invoice_debt(texto)
    fecha_vencimiento = parse_invoice_debt_date(texto)
    asunto = parse_invoice_subject(texto)
    concepto = find_concepts_keys(texto)
    print(f"\nTotal a pagar: {factura:.2f}€")
    print(f"Fecha de vencimiento: {fecha_vencimiento}")
    print(f"Asunto/Concepto: {asunto}")
    print(f"Concepto clave identificado: {concepto}")
