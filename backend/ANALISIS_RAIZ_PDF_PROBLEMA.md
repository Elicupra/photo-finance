# 🔍 Análisis Profundo - Problema de Extracción de Texto en PDFs

**Fecha:** 17 de Febrero, 2026  
**Problema:** Los PDFs retornan contenido de texto vacío durante la extracción  

---

## 🎯 Root Cause Identificada

### Hallazgo Principal
**Los PDFs son documentos basados en IMÁGENES, no en texto vectorial.**

### Evidencia Diagnóstica

| Aspecto | Estado | Detalle |
|---------|--------|---------|
| **Encriptación** | ❌ NO | Los PDFs no están protegidos |
| **Contenido de Texto** | ❌ NO | 0 caracteres en todas las páginas |
| **Imágenes Rasterizadas** | ✅ SÍ | Todos tienen XObject (imágenes embebidas) |
| **Fuentes Embebidas** | ✅ SÍ | Tienen recursos /Font pero sin contenido de texto |
| **Generador** | Quadient Inspire | Software de generación de documentos que rasteriza |

### Análisis por PDF

```
Naturgy_01_25.pdf (6 páginas)
  ├─ Página 1: Imágenes ✓, Texto ✗, 595x842 px
  ├─ Página 2: Imágenes ✗, Texto ✗, 595x842 px
  ├─ Página 3: Imágenes ✓, Texto ✗, 595x842 px
  ├─ Página 4: Imágenes ✓, Texto ✗, 595x842 px
  ├─ Página 5: Imágenes ✓, Texto ✗, 595x842 px
  └─ Página 6: Imágenes ✓, Texto ✗, 595x842 px

Naturgy_01_26.pdf (4 páginas)
  ├─ Página 1: Imágenes ✓, Texto ✗, 595x842 px
  ├─ Página 2: Imágenes ✓, Texto ✗, 595x842 px
  ├─ Página 3: Imágenes ✓, Texto ✗, 595x842 px
  └─ Página 4: Imágenes ✓, Texto ✗, 595x842 px

[Mismo patrón para Naturgy_02_25.pdf, Naturgy_03_25.pdf, Naturgy_04_25.pdf]
```

---

## ❌ Por Qué PyPDF2 NO Funciona

### Tipo de PDF
Los PDFs de Naturgy son de dos tipos:

1. **PDF Rasterizado (Type 1):** La página COMPLETA es una imagen
   - Todo el contenido (texto, gráficos, etc.) está en formato de imagen
   - PyPDF2 NO puede extraer texto de imágenes

2. **PDF Híbrido (Type 2):** Contiene imágenes + objetos de texto
   - El contenido gráfico es una imagen
   - El "texto" visible también está como parte de la imagen
   - PyPDF2 no encuentra objetos de texto extractables

### Limitación de PyPDF2
```python
# Lo que PyPDF2 intenta hacer:
text = page.extract_text()
# Busca en: /Contents → objeto de stream → texto codificado
# SI NO encuentra objetos de texto → retorna vacío o None
```

**PyPDF2 es excelente para:**
- ✓ PDFs nativos con texto vectorial (Word, LaTeX exportado)
- ✓ Documentos digitales creados directamente en PDF

**PyPDF2 NO sirve para:**
- ✗ PDFs escaneados
- ✗ PDFs rasterizados
- ✗ PDFs generados por software como Quadient que rasteriza

---

## 🛠️ SOLUCIONES ALTERNATIVAS EN PYTHON

### Opción 1: OCR (Optical Character Recognition) - RECOMENDADO

#### 1.1. **Tesseract + pytesseract** (Gratuito, Open-source)

**Ventajas:**
- Totalmente gratuito y open-source
- Excelente precisión
- Soporta más de 100 idiomas
- Instalación local

**Desventajas:**
- Requiere instalación de Tesseract (ejecutable externo)
- Más lento que alternativas en la nube

**Instalación:**
```bash
# 1. Descargar Tesseract OCR
# https://github.com/UB-Mannheim/tesseract/wiki

# 2. Instalar biblioteca Python
pip install pytesseract
pip install pdf2image  # Para convertir PDF a imágenes
pip install Pillow
```

**Código Ejemplo:**
```python
import pytesseract
from pdf2image import convert_from_path
from PIL import Image

def extract_text_with_tesseract(pdf_path):
    """Extrae texto usando OCR (Tesseract)"""
    # Convertir PDF a imágenes
    images = convert_from_path(pdf_path)
    
    full_text = ""
    for page_num, image in enumerate(images):
        # Aplicar OCR usando Tesseract
        text = pytesseract.image_to_string(image, lang='spa')
        full_text += f"\n--- Página {page_num + 1} ---\n{text}"
    
    return full_text

# Uso
texto = extract_text_with_tesseract("Naturgy_01_25.pdf")
print(texto)
```

**Precisión esperada:**
- Spanish OCR: 85-95% con buenos escaneos
- Textos claros: 95%+
- Documentos de facturación: ~90%

---

#### 1.2. **EasyOCR** (Moderno, Basado en Deep Learning)

**Ventajas:**
- Basado en redes neuronales (mejor precisión)
- Fácil de usar
- Multilenguaje
- Mejor con documentos complejos

**Desventajas:**
- Requiere descargar modelos (~100 MB primera vez)
- Un poco más lento

**Código:**
```python
import easyocr
from pdf2image import convert_from_path

def extract_with_easyocr(pdf_path):
    """Extrae texto con EasyOCR"""
    reader = easyocr.Reader(['es'])  # Spanish
    images = convert_from_path(pdf_path)
    
    full_text = ""
    for page_num, image in enumerate(images):
        results = reader.readtext(image)
        text = "\n".join([text for (_, text, _) in results])
        full_text += f"\n--- Página {page_num + 1} ---\n{text}"
    
    return full_text

# Instalación
# pip install easyocr opencv-python-headless
```

---

### Opción 2: APIs en la Nube (Más Precisas, Pago)

#### 2.1. **Google Vision API**

**Precisión:** 97-99%  
**Costo:** ~$1.50 por 1000 páginas

```python
from google.cloud import vision
from pdf2image import convert_from_path

def extract_with_google_vision(pdf_path):
    """Extrae texto usando Google Cloud Vision"""
    client = vision.ImageAnnotatorClient()
    images = convert_from_path(pdf_path)
    
    full_text = ""
    for page_num, image in enumerate(images):
        # Convertir imagen a bytes
        image_bytes = image.tobytes()
        
        image_obj = vision.Image(content=image_bytes)
        response = client.document_text_detection(image=image_obj)
        
        text = response.full_text_annotation.text
        full_text += f"\n--- Página {page_num + 1} ---\n{text}"
    
    return full_text
```

**Setup:**
```bash
pip install google-cloud-vision
# Luego configurar credenciales de GCP
```

---

#### 2.2. **AWS Textract**

**Precisión:** 97-99%  
**Costo:** Similar a Google Vision

```python
import boto3
from pdf2image import convert_from_path

def extract_with_aws_textract(pdf_path):
    """Extrae texto usando AWS Textract"""
    client = boto3.client('textract', region_name='us-east-1')
    
    with open(pdf_path, 'rb') as f:
        response = client.detect_document_text(
            Document={'Bytes': f.read()}
        )
    
    # Procesar respuesta
    text = ""
    for block in response['Blocks']:
        if block['BlockType'] == 'LINE':
            text += block['Text'] + '\n'
    
    return text
```

---

### Opción 3: Bibliotecas Alternativas de Extracción

#### 3.1. **pdfminer.six** (Extracción avanzada)

```python
from pdfminer.high_level import extract_text

# Intenta extraer de PDFs con texto
text = extract_text("Naturgy_01_25.pdf")
```

**Nota:** También fallaría con PDFs rasterizados, pero es más flexible que PyPDF2.

---

#### 3.2. **pdfplumber** (Análisis estructurado)

```python
import pdfplumber

with pdfplumber.open("Naturgy_01_25.pdf") as pdf:
    for page in pdf.pages:
        text = page.extract_text()
        print(text)
```

---

### Opción 4: Conversión + Procesamiento

**Flujo Completo (Recomendado):**

```python
import pytesseract
from pdf2image import convert_from_path
from pathlib import Path
import json

def extract_and_process_pdf_complete(pdf_path):
    """
    Extrae texto de PDF rasterizado
    Retorna estructura JSON similar al PDFExtractor actual
    """
    
    # Convertir PDF a imágenes
    images = convert_from_path(pdf_path)
    
    document_data = {
        'nombre_archivo': Path(pdf_path).name,
        'ruta_archivo': str(Path(pdf_path).absolute()),
        'num_paginas': len(images),
        'titulo': None,
        'autor': None,
        'fecha_creacion': None,
        'paginas': [],
        'metodo_extraccion': 'OCR (Tesseract)',
        'precision_estimada': '90%'
    }
    
    for page_num, image in enumerate(images):
        # OCR
        text = pytesseract.image_to_string(image, lang='spa')
        
        # Limpiar espacios en blanco
        text = text.strip()
        
        document_data['paginas'].append({
            'numero_pagina': page_num + 1,
            'contenido': text,
            'bytes_imagen': len(image.tobytes())
        })
    
    return document_data

# Uso
resultado = extract_and_process_pdf_complete("Naturgy_01_25.pdf")
print(json.dumps(resultado, indent=2, ensure_ascii=False))

# Guardar resultado
with open("Naturgy_01_25_ocr.json", "w", encoding="utf-8") as f:
    json.dump(resultado, f, indent=2, ensure_ascii=False)
```

---

## 📊 Comparativa de Soluciones

| Solución | Precisión | Velocidad | Costo | Configuración | Recomendado |
|----------|-----------|-----------|-------|---------------|-------------|
| **Tesseract + pytesseract** | 85-95% | Medio | Gratis | Local | ✓ Para producción local |
| **EasyOCR** | 90-96% | Medio | Gratis | Fácil | ✓ Para precisión mejorada |
| **Google Vision** | 97-99% | Rápido | $0.0015/pág | Cloud | ✓ Para máxima precisión |
| **AWS Textract** | 97-99% | Rápido | $0.0015/pág | Cloud | ✓ Para máxima precisión |
| **pdfminer.six** | 0% | Rápido | Gratis | Fácil | ✗ No funciona |
| **pdfplumber** | 0% | Rápido | Gratis | Fácil | ✗ No funciona |

---

## 🚀 RECOMENDACIÓN FINAL

### Para el Proyecto Photo-Finance

**Fase 1 - Implementar Local (Corto Plazo):**
```
1. Instalar: pytesseract + Tesseract OCR
2. Crear PDFOCRExtractor que herede de PDFExtractor
3. Usar para archivos rasterizados
4. Costo: 0€ (open-source)
5. Precisión: 90-95%
```

**Fase 2 - Mejorar Precisión (Mediano Plazo):**
```
1. Migrar a EasyOCR (redes neuronales)
2. Entrenar modelo específico para facturas Naturgy
3. Costo: 0€ (open-source)
4. Precisión: 95%+
```

**Fase 3 - Máxima Confiabilidad (Producción):**
```
1. Usar Google Vision API o AWS Textract
2. Para documentos críticos (facturas)
3. Costo: ~$0.45 por 1000 facturas
4. Precisión: 97-99%
```

---

## 📝 Implementación Sugerida

### Estructura Recomendada:

```
backend/
├── extractors/
│   ├── pdf_extractor.py (MANTENER - para PDFs nativos)
│   ├── pdf_ocr_extractor.py (NUEVO - para PDFs rasterizados)
│   └── pdf_hybrid_extractor.py (NUEVO - detecta tipo y elige método)
└── test/
    ├── test_pdf_extractor.py
    └── test_pdf_ocr_extractor.py
```

### Detector Automático:

```python
class PDFHybridExtractor:
    """Extractor que detecta el tipo de PDF y elige el método"""
    
    def __init__(self, pdf_path):
        self.pdf_path = pdf_path
        self._detect_type()
    
    def _detect_type(self):
        # Si tiene texto extractable → usa PDFExtractor
        # Si no → usa PDFOCRExtractor
        pass
    
    def extract_full_document(self):
        # Delega al extractor apropiado
        pass
```

---

## 🎓 Conclusión

**El problema NO es un bug del código**, sino una limitación técnica:

| Hecho | Verdad |
|------|--------|
| ✓ El código PDFExtractor funciona correctamente | ✓ Es estable y robusto |
| ✓ Los PDFs se cargan correctamente | ✓ Sin protección |
| ✗ PyPDF2 NO puede extraer de PDFs rasterizados | ✗ Es una limitación conocida |
| ✓ Solución: Usar OCR | ✓ Mejora inmediata disponible |

**Los PDFs de Naturgy son documentos generados por software empresarial (Quadient) que los rasteriza completamente durante la generación. Para extraer información, necesitas OCR (Optical Character Recognition).**

