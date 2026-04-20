"""Proceso para iniciar backend de lectura de PDFs
Llamada a endpoints FastAPI
Llamada a funciones de procesamiento de PDFs con EasyOCR
Guardado de PDFs procesados en la base de datos"""

import easyocr
import requests
import os
import dotenv
import sys
import base64
from components.extract_pdf import extract_pdf, text_to_json, parse_pdf_text

from fastapi import FastAPI, UploadFile, File 

dotenv.load_dotenv()
CORS_ORIGINS = ["http://localhost:3000"]
app = FastAPI(title="PDF Reader Backend")

# Configuración de CORS
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


### PRUEBA PDF
# Force UTF-8 output on Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

#dotenv.load_dotenv()
pdf_file = "Naturgy_08_25.pdf"
pdf_folder = "container_pdf"
pdf_path = os.path.join(pdf_folder, pdf_file)
 # Cambia esto al código de idioma que necesites (por ejemplo, 'en' para inglés)
###



# Configuración de EasyOCR
reader = easyocr.Reader(['es', 'en'])

# Endpoint para procesar PDF
@app.post("/process-pdf/")
# Endpoint que lee la ruta del pdf y devuelve el texto extraído
async def process_pdf(file: UploadFile = pdf_path):
    # Guardar el archivo PDF temporalmente
    try:
        contents = await file.read()
        temp_path = f"/tmp/{file.filename}"
        with open(temp_path, "wb") as f:
            f.write(contents)
        
        # Extraer texto del PDF
        extracted_text = extract_pdf(temp_path, lenguaje='es', use_tesseract=True)
        
        # Guardar el PDF procesado en la base de datos (simulado aquí)
        # Aquí podrías agregar lógica para guardar el PDF y el texto extraído en tu base de datos

        # Eliminar el archivo temporal
        os.remove(temp_path)
        
        return {"extracted_text": extracted_text}
    except Exception as e:
        return {"error": str(e)}

# Endpoint para procesar texto extraído y devolver datos estructurados
@app.post("/process-text/")
async def process_text(extracted_text: str):
    try:
        cleaned_text = parse_pdf_text.limpiar_texto(text)
        concept = parse_pdf_text.parse_invoice_debt(cleaned_text)
        debt = parse_pdf_text.parse_invoice_debt(cleaned_text)
        type_invoice = parse_pdf_text.find_invoice_type(cleaned_text)
        # Convertir a JSON estructurado
        json_data = text_to_json(cleaned_text, concept, debt, type_invoice)
        
        return {"status": "success", "structured_data": json_data}
    except Exception as e:
        return {"error": str(e)}

#TODO: Agregar más endpoints según sea necesario, por ejemplo, para guardar datos en la base de datos, listar PDFs procesados, etc.
# Endpoint para guardar la informacion del PDF procesado en la base de datos (simulado aquí)