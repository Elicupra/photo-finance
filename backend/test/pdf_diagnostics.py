"""
Analizador Avanzado de PDFs
Diagnóstico profundo para entender por qué no se extrae el texto
"""
import sys
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

import PyPDF2


class PDFDiagnostics:
    """Clase para diagnosticar problemas con PDFs"""
    
    def __init__(self, pdf_path: Path):
        self.pdf_path = Path(pdf_path)
        self.reader = None
        self.file_handle = None
        self._load_pdf()
    
    def _load_pdf(self):
        """Carga el PDF manteniendo el archivo abierto"""
        self.file_handle = open(self.pdf_path, 'rb')
        self.reader = PyPDF2.PdfReader(self.file_handle)
    
    def __del__(self):
        """Cierra el archivo al destruir el objeto"""
        if self.file_handle:
            self.file_handle.close()
    
    def analyze_structure(self) -> Dict[str, Any]:
        """Analiza la estructura del PDF"""
        analysis = {
            'archivo': self.pdf_path.name,
            'es_encriptado': self.reader.is_encrypted,
            'num_paginas': len(self.reader.pages),
            'metadatos': self._get_metadata(),
            'info_documento': self._get_document_info(),
            'paginas_detalles': []
        }
        return analysis
    
    def _get_metadata(self) -> Dict:
        """Extrae metadatos del PDF"""
        metadata = {
            'titulo': None,
            'autor': None,
            'fecha_creacion': None,
            'sujeto': None,
            'palabras_clave': None,
            'productor': None,
            'creador': None
        }
        
        try:
            if self.reader.metadata:
                metadata['titulo'] = self.reader.metadata.title
                metadata['autor'] = self.reader.metadata.author
                metadata['fecha_creacion'] = str(self.reader.metadata.creation_date)
                metadata['sujeto'] = self.reader.metadata.subject
                metadata['palabras_clave'] = self.reader.metadata['/Keywords'] if '/Keywords' in self.reader.metadata else None
                metadata['productor'] = self.reader.metadata['/Producer'] if '/Producer' in self.reader.metadata else None
                metadata['creador'] = self.reader.metadata['/Creator'] if '/Creator' in self.reader.metadata else None
        except Exception as e:
            print(f"Error extrayendo metadatos: {e}")
        
        return metadata
    
    def _get_document_info(self) -> Dict:
        """Obtiene información general del documento"""
        info = {
            'es_pdf_basado_texto': False,
            'es_pdf_escaneado': False,
            'explicacion': ''
        }
        
        try:
            # Intentar extraer texto de la primera página
            if len(self.reader.pages) > 0:
                page = self.reader.pages[0]
                text = page.extract_text() or ""
                
                if text and len(text.strip()) > 10:
                    info['es_pdf_basado_texto'] = True
                    info['explicacion'] = "PDF con contenido de texto numérico"
                else:
                    # Verificar si tiene imágenes
                    try:
                        if "/Resources" in page and "/XObject" in page["/Resources"]:
                            info['es_pdf_escaneado'] = True
                            info['explicacion'] = "PDF con imágenes (posiblemente escaneado)"
                        else:
                            info['explicacion'] = "PDF sin contenido de texto extractable. Posiblemente protegido o codificado"
                    except:
                        info['explicacion'] = "PDF sin contenido de texto extractable"
        except Exception as e:
            info['explicacion'] = f"Error al analizar: {str(e)}"
        
        return info
    
    def analyze_pages_detailed(self) -> List[Dict]:
        """Analiza cada página en detalle"""
        pages_analysis = []
        
        for page_num, page in enumerate(self.reader.pages):
            page_info = {
                'numero_pagina': page_num + 1,
                'tiene_contenido_texto': False,
                'caracteres_extraidos': 0,
                'tiene_imagenes': False,
                'tiene_anotaciones': False,
                'rotacion': 0,
                'recursos': [],
                'tamano_pagina': None,
                'compresion': None,
                'contenido_raw_length': 0
            }
            
            # Texto
            try:
                text = page.extract_text() or ""
                if text and len(text.strip()) > 0:
                    page_info['tiene_contenido_texto'] = True
                    page_info['caracteres_extraidos'] = len(text.strip())
            except Exception as e:
                pass
            
            # Imágenes y otros recursos
            try:
                if "/Resources" in page:
                    resources = page["/Resources"]
                    if resources:
                        if "/XObject" in resources:
                            page_info['tiene_imagenes'] = True
                            page_info['recursos'].append('XObject (Imágenes)')
                        if "/Font" in resources:
                            page_info['recursos'].append('Font (Fuentes)')
                        if "/ColorSpace" in resources:
                            page_info['recursos'].append('ColorSpace')
            except Exception as e:
                pass
            
            # Anotaciones
            try:
                if "/Annots" in page:
                    page_info['tiene_anotaciones'] = True
            except Exception as e:
                pass
            
            # Tamaño de página
            try:
                if "/MediaBox" in page:
                    mediabox = page["/MediaBox"]
                    page_info['tamano_pagina'] = f"{float(mediabox[2]):.0f}x{float(mediabox[3]):.0f}"
            except Exception as e:
                pass
            
            # Rotación
            try:
                if "/Rotate" in page:
                    page_info['rotacion'] = page["/Rotate"]
            except Exception as e:
                pass
            
            pages_analysis.append(page_info)
        
        return pages_analysis


def run_diagnostics():
    """Ejecuta diagnóstico en todos los PDFs"""
    pdf_dir = Path(__file__).parent.parent / "pdfs"
    pdf_files = sorted(pdf_dir.glob("*.pdf"))
    
    print("\n" + "=" * 80)
    print("🔍 ANÁLISIS AVANZADO DE PDFs")
    print("=" * 80 + "\n")
    
    from datetime import datetime
    all_diagnostics = {
        'fecha': datetime.now().isoformat(),
        'pdfs_analizados': []
    }
    
    for pdf_file in pdf_files:
        print(f"\n📄 Analizando: {pdf_file.name}")
        print("-" * 80)
        
        try:
            diagnostics = PDFDiagnostics(pdf_file)
            
            # Análisis general
            structure = diagnostics.analyze_structure()
            print(f"✓ Encriptado: {structure['es_encriptado']}")
            print(f"✓ Número de páginas: {structure['num_paginas']}")
            print(f"✓ Tipo de documento: {structure['info_documento']['explicacion']}")
            
            # Metadatos
            print("\n📋 Metadatos:")
            metadata = structure['metadatos']
            print(f"  - Título: {metadata['titulo']}")
            print(f"  - Autor: {metadata['autor']}")
            print(f"  - Productor: {metadata['productor']}")
            print(f"  - Creador: {metadata['creador']}")
            
            # Análisis de páginas
            pages_analysis = diagnostics.analyze_pages_detailed()
            print(f"\n📑 Análisis por Página:")
            
            for page in pages_analysis:
                print(f"\n  Página {page['numero_pagina']}:")
                print(f"    - Contenido de texto: {'✓ SÍ' if page['tiene_contenido_texto'] else '✗ NO'}")
                print(f"    - Caracteres extraídos: {page['caracteres_extraidos']}")
                print(f"    - Tiene imágenes: {'✓ SÍ' if page['tiene_imagenes'] else '✗ NO'}")
                print(f"    - Recursos: {', '.join(page['recursos']) if page['recursos'] else 'Ninguno'}")
                print(f"    - Tamaño página: {page['tamano_pagina']}")
                if page['rotacion'] != 0:
                    print(f"    - Rotación: {page['rotacion']}°")
            
            structure['paginas_detalles'] = pages_analysis
            all_diagnostics['pdfs_analizados'].append(structure)
            
        except Exception as e:
            print(f"❌ Error analizando {pdf_file.name}: {str(e)}")
    
    # Resumen final
    print("\n" + "=" * 80)
    print("📊 RESUMEN DEL DIAGNÓSTICO")
    print("=" * 80 + "\n")
    
    pdfs_basados_texto = 0
    pdfs_escaneados = 0
    
    for pdf in all_diagnostics['pdfs_analizados']:
        if pdf['info_documento']['es_pdf_basado_texto']:
            pdfs_basados_texto += 1
        elif pdf['info_documento']['es_pdf_escaneado']:
            pdfs_escaneados += 1
    
    print(f"PDFs con contenido de texto: {pdfs_basados_texto}")
    print(f"PDFs escaneados (imágenes): {pdfs_escaneados}")
    print(f"PDFs sin contenido extractable: {len(all_diagnostics['pdfs_analizados']) - pdfs_basados_texto - pdfs_escaneados}")
    
    return all_diagnostics


if __name__ == "__main__":
    diagnostics = run_diagnostics()
