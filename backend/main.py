"""Proceso para iniciar backend de lectura de PDFs
Llamada a endpoints FastAPI
Llamada a funciones de procesamiento de PDFs con EasyOCR
Guardado de PDFs procesados en la base de datos"""

import easyocr
import requests
import os
import dotenv
import base64

from pdf2image import convert_from_path
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
    try:
