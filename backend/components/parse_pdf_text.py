# parse_pdf_text.py -- Funciones para procesar el texto extraído de PDFs y convertirlo a JSON
# Entrada de texto extraído, salida de datos estructurados (conceptos, importes, fechas)

import json

import re
from typing import Dict, Any, List, Optional
import datetime
from decimal import Decimal, InvalidOperation

def limpiar_texto(texto: str) -> str:
    """
    Limpia el texto extraído del PDF eliminando caracteres no deseados
    y normalizando espacios y saltos de línea.
    """
    # Reemplazar múltiples espacios por uno solo
    texto = re.sub(r'\s+', ' ', texto)
    # Eliminar caracteres de control excepto saltos de línea
    texto = re.sub(r'[^\x20-\x7E\n]+', '', texto)
    # Normalizar saltos de línea
    texto = re.sub(r'\n+', '\n', texto)
    return texto.strip()

def parse_invoice_debt(text: str):
    """
    Procesa el texto extraído para identificar conceptos e importes.
    """
    patrones = [
        r'TOTAL\s+A\s+PAGAR\s*:?\s*([0-9][0-9\.,]{0,10})\s*€?',
        r'IMPORTE\s+TOTAL\s*:?\s*([0-9][0-9\.,]{0,10})\s*€?',
        r'TOTAL\s+SERVICIOS\s*:?\s*([0-9][0-9\.,]{0,10})\s*€?',
    ]

    for patron in patrones:
        match = re.search(patron, text, re.IGNORECASE)
        if not match:
            continue

        raw_amount = re.sub(r'\s+', '', match.group(1))
        if not raw_amount:
            continue

        # Normaliza separadores de miles/decimales para tolerar OCR variable.
        if ',' in raw_amount and '.' in raw_amount:
            if raw_amount.rfind(',') > raw_amount.rfind('.'):
                normalized = raw_amount.replace('.', '').replace(',', '.')
            else:
                normalized = raw_amount.replace(',', '')
        elif ',' in raw_amount:
            normalized = raw_amount.replace('.', '').replace(',', '.')
        else:
            normalized = raw_amount.replace(',', '')

        try:
            return float(normalized)
        except ValueError:
            continue

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

