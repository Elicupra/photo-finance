# text_to_json.py -- Función para convertir texto extraído a formato JSON
# Entrada de texto extraído, salida de JSON con el texto estructurado para frontend

import json

def text_to_json(concept: str, debt: float, type_invoice: str) -> dict:
    """Convierte el texto extraído a formato JSON
    Args:        
        concept (str): Concepto extraído del PDF
        debt (float): Deuda extraída del PDF
        type_invoice (str): Tipo de factura extraído del PDF
    Returns:        
        dict: Diccionario con el texto estructurado para frontend"""
    # Aquí se puede agregar lógica para estructurar el texto según las necesidades del frontend
    # Concepto
    concept = concept.strip() if concept else "No especificado"
    
    # Deuda
    debt = float(debt) if debt else 0.0
    
    # Tipo de factura
    type_invoice = type_invoice.strip() if type_invoice else "No especificado"
    
    # Crear estructura JSON
    json_output = {
        "concepto": concept,
        "deuda": debt,
        "tipo_factura": type
    }
    return json_output   


    