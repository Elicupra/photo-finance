"""Utilidades para el manejo del resto de modulos"""

import easyocr
import requests
import os
import dotenv


dotenv.load_dotenv()
# Configuración de EasyOCR

#Funcion para devolver el texto extraido del PDF a JSON
def text_to_json(text):
    """Convierte el texto extraído a formato JSON"""
    return {"extracted_text": text}

__if__ main = "__main__":
      pass
