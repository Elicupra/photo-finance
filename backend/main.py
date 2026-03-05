"""Proceso para iniciar backend de lectura de PDFs
Llamada a endpoints FastAPI
Llamada a funciones de procesamiento de PDFs con EasyOCR
Guardado de PDFs procesados en la base de datos"""

import easyocr
import requests
import os
import dotenv
import base64
from extract_pdf import extract_pdf
from utils import text_to_json

from fastapi import FastAPI, UploadFile, File 

dotenv.load_dotenv()
CORS_ORIGINS = ["http://localhost:3000"]
app = FastAPI(title="PDF Reader Backend")

# Configuración de CORS
from fastapi.middleware.cors import CORSMiddlewareapp.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuración de EasyOCR
reader = easyocr.Reader(['es', 'en'])

# Endpoint para procesar PDF
@app.post("/process-pdf/")
async def process_pdf(file: UploadFile = File(...)):
    # Guardar el archivo PDF temporalmente
    try:
        contents = await file.read()
        temp_path = f"/tmp/{file.filename}"
        with open(temp_path, "wb") as f:
            f.write(contents)
        
        # Extraer texto del PDF
        extracted_text = extract_pdf(temp_path)
        
        # Guardar el PDF procesado en la base de datos (simulado aquí)
        # Aquí podrías agregar lógica para guardar el PDF y el texto extraído en tu base de datos

        # Eliminar el archivo temporal
        os.remove(temp_path)
        
        return {"extracted_text": extracted_text}
    except Exception as e:
        return {"error": str(e)}
    
# Endpoint para devolver a Frontend el texto extraído
@app.get("/show-text/")
def show_text():
