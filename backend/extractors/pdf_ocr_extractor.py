"""
PASO 4: PDF OCR Extractor - Extrae texto de PDFs rasterizados usando OCR
Clase para extraer texto de archivos PDF basados en imágenes (rasterizados)
"""
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import json


class PDFOCRExtractor:
    """
    Extractor de contenido de PDFs rasterizados usando OCR
    
    Soporta dos métodos:
    1. Tesseract OCR (local, requiere instalación)
    2. EasyOCR (GPU acelerado, mejor precisión)
    """
    
    OCR_METHODS = {
        'tesseract': 'pytesseract',
        'easyocr': 'easyocr',
        'google_vision': 'google-cloud-vision',
        'aws_textract': 'boto3'
    }
    
    def __init__(self, pdf_path: Path, method: str = 'tesseract', language: str = 'spa'):
        """
        Inicializa el extractor OCR
        
        Args:
            pdf_path: Ruta al archivo PDF
            method: Método OCR a usar ('tesseract', 'easyocr')
            language: Código de idioma ('spa' para español, 'eng' para inglés)
        """
        self.pdf_path = Path(pdf_path)
        self.method = method
        self.language = language
        self.ocr_reader = None
        self._initialize_ocr()
    
    def _initialize_ocr(self):
        """Inicializa el motor OCR seleccionado"""
        if self.method == 'tesseract':
            self._init_tesseract()
        elif self.method == 'easyocr':
            self._init_easyocr()
        else:
            raise ValueError(f"Método OCR no soportado: {self.method}")
    
    def _init_tesseract(self):
        """Inicializa Tesseract OCR"""
        try:
            import pytesseract
            self.pytesseract = pytesseract
            # Verificar que Tesseract esté instalado
            pytesseract.pytesseract.get_tesseract_version()
        except ImportError:
            raise ImportError(
                "pytesseract no está instalado. Instala con: pip install pytesseract\n"
                "También requiere Tesseract OCR: https://github.com/UB-Mannheim/tesseract/wiki"
            )
        except Exception as e:
            raise RuntimeError(
                f"Tesseract OCR no está disponible: {str(e)}\n"
                "Descárga desde: https://github.com/UB-Mannheim/tesseract/wiki"
            )
    
    def _init_easyocr(self):
        """Inicializa EasyOCR"""
        try:
            import easyocr
            print(f"Cargando modelo EasyOCR para idioma: {self.language}...")
            self.ocr_reader = easyocr.Reader([self.language], gpu=False)
        except ImportError:
            raise ImportError(
                "easyocr no está instalado. Instala con: pip install easyocr"
            )
        except Exception as e:
            raise RuntimeError(f"Error inicializando EasyOCR: {str(e)}")
    
    def _convert_pdf_to_images(self) -> List:
        """Convierte PDF a lista de imágenes PIL"""
        try:
            from pdf2image import convert_from_path
        except ImportError:
            raise ImportError(
                "pdf2image no está instalado. Instala con: pip install pdf2image"
            )
        
        try:
            images = convert_from_path(self.pdf_path, dpi=300)
            return images
        except Exception as e:
            raise ValueError(f"Error convirtiendo PDF a imágenes: {str(e)}")
    
    def extract_text_from_image(self, image) -> str:
        """
        Extrae texto de una imagen usando OCR
        
        Args:
            image: Imagen PIL
        
        Returns:
            Texto extraído
        """
        try:
            if self.method == 'tesseract':
                text = self.pytesseract.image_to_string(
                    image,
                    lang=self.language,
                    config='--psm 1'  # Assume single uniform block
                )
            elif self.method == 'easyocr':
                results = self.ocr_reader.readtext(image)
                # Extraer texto de los resultados
                text = "\n".join([text for (_, text, confidence) in results if confidence > 0.3])
            
            return text.strip() if text else ""
        except Exception as e:
            print(f"Error extrayendo texto con {self.method}: {str(e)}")
            return ""
    
    def extract_metadata(self) -> Dict[str, Optional[str]]:
        """
        Extrae metadatos del PDF (si existen)
        
        Returns:
            Dict con metadatos
        """
        metadata = {
            'titulo': None,
            'autor': None,
            'fecha_creacion': None,
            'metodo_extraccion': f'OCR ({self.method})',
            'idioma_ocr': self.language
        }
        
        try:
            # Intentar obtener metadatos de PyPDF2
            import PyPDF2
            with open(self.pdf_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                if reader.metadata:
                    metadata['titulo'] = reader.metadata.title
                    metadata['autor'] = reader.metadata.author
                    metadata['fecha_creacion'] = str(reader.metadata.creation_date)
        except Exception as e:
            print(f"Advertencia: No se pudieron obtener metadatos: {str(e)}")
        
        return metadata
    
    def get_num_pages(self) -> int:
        """
        Obtiene el número de páginas del PDF
        
        Returns:
            int: Número de páginas
        """
        try:
            import PyPDF2
            with open(self.pdf_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                return len(reader.pages)
        except Exception as e:
            # Fallback: convertir a imágenes para contar
            try:
                images = self._convert_pdf_to_images()
                return len(images)
            except:
                raise ValueError(f"Error obteniendo número de páginas: {str(e)}")
    
    def extract_all_pages(self) -> List[Dict[str, any]]:
        """
        Extrae el texto de todas las páginas usando OCR
        
        Returns:
            Lista de diccionarios con número de página y contenido
        """
        pages = []
        
        try:
            images = self._convert_pdf_to_images()
            
            print(f"Procesando {len(images)} páginas con {self.method} OCR...")
            
            for page_num, image in enumerate(images, start=1):
                print(f"  Extrayendo página {page_num}/{len(images)}...", end=' ')
                
                content = self.extract_text_from_image(image)
                
                pages.append({
                    'numero_pagina': page_num,
                    'contenido': content,
                    'caracteres': len(content),
                    'metodo_ocr': self.method
                })
                
                print(f"✓ ({len(content)} caracteres)")
            
        except Exception as e:
            print(f"Error extrayendo páginas: {str(e)}")
            raise
        
        return pages
    
    def extract_full_document(self) -> Dict:
        """
        Extrae toda la información del documento
        
        Returns:
            Dict con toda la información del documento
        """
        metadata = self.extract_metadata()
        pages = self.extract_all_pages()
        
        return {
            'nombre_archivo': self.pdf_path.name,
            'ruta_archivo': str(self.pdf_path.absolute()),
            'num_paginas': len(pages),
            'titulo': metadata.get('titulo'),
            'autor': metadata.get('autor'),
            'fecha_creacion': metadata.get('fecha_creacion'),
            'paginas': pages,
            'metodo_extraccion': f'OCR ({self.method})',
            'idioma_ocr': self.language,
            'fecha_procesamiento': datetime.now().isoformat()
        }


def extract_pdf_with_ocr(pdf_path: Path, method: str = 'tesseract', language: str = 'spa') -> Dict:
    """
    Función auxiliar para extraer un PDF con OCR
    
    Args:
        pdf_path: Ruta al archivo PDF
        method: Método OCR ('tesseract' o 'easyocr')
        language: Código de idioma
    
    Returns:
        Dict con la información extraída
    """
    extractor = PDFOCRExtractor(pdf_path, method=method, language=language)
    return extractor.extract_full_document()


# ===== Script de demostración =====

if __name__ == "__main__":
    """
    Script de demostración de extracción OCR
    
    Instrucciones de instalación de dependencias:
    
    1. Opción A - Tesseract (Recomendado para pruebas):
       - Windows: Descargar MSI desde https://github.com/UB-Mannheim/tesseract/wiki
       - Mac/Linux: brew install tesseract
       - Luego: pip install pytesseract pdf2image Pillow
    
    2. Opción B - EasyOCR (Mejor precisión):
       - pip install easyocr pdf2image opencv-python-headless
    """
    
    print("\n" + "=" * 80)
    print("🔤 PDF OCR EXTRACTOR - Demostración")
    print("=" * 80 + "\n")
    
    pdf_dir = Path(__file__).parent.parent / "pdfs"
    pdf_files = sorted(pdf_dir.glob("*.pdf"))
    
    if not pdf_files:
        print("❌ No se encontraron archivos PDF en backend/pdfs/")
        print("\nPara usar OCR:")
        print("1. Instala las dependencias (ver arriba)")
        print("2. Ejecuta este script nuevamente")
        exit(1)
    
    # Seleccionar primer PDF
    pdf_path = pdf_files[0]
    
    print(f"📄 Archivo: {pdf_path.name}")
    print(f"📁 Ruta: {pdf_path}\n")
    
    print("⚠️  NOTA: Para usar OCR, primero debes instalar las dependencias.\n")
    
    print("Opción 1 - Tesseract (Gratuito):")
    print("  pip install pytesseract pdf2image Pillow")
    print("  Luego descargar Tesseract desde:")
    print("  https://github.com/UB-Mannheim/tesseract/wiki\n")
    
    print("Opción 2 - EasyOCR (Mejor precisión):")
    print("  pip install easyocr pdf2image opencv-python-headless\n")
    
    # Intentar con Tesseract si está disponible
    try:
        print("Intentando con Tesseract OCR...\n")
        resultado = extract_pdf_with_ocr(pdf_path, method='tesseract', language='spa')
        
        # Guardar resultado
        output_file = Path(__file__).parent / "test_results" / f"{pdf_path.stem}_ocr_result.json"
        output_file.parent.mkdir(exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(resultado, f, indent=2, ensure_ascii=False)
        
        print(f"\n✓ Extracción completada!")
        print(f"✓ Resultado guardado en: {output_file}")
        print(f"\n📊 Resumen:")
        print(f"   - Páginas procesadas: {resultado['num_paginas']}")
        print(f"   - Método OCR: {resultado['metodo_extraccion']}")
        print(f"   - Idioma: {resultado['idioma_ocr']}")
        
        # Mostrar primera página
        if resultado['paginas']:
            primera_pagina = resultado['paginas'][0]
            print(f"\n   Primera página ({primera_pagina['caracteres']} caracteres):")
            contenido = primera_pagina['contenido'][:200]
            print(f"   {contenido}...")
    
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        print("\nInstalaPrimero las dependencias siguiendo las instrucciones arriba.")
