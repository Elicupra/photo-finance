"""
Test del PDFExtractor con generación de reportes JSON
Ejecuta validaciones y genera salida en archivos JSON
"""
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

# Agregar el directorio backend al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from extractors.pdf_extractor import PDFExtractor, extract_pdf


class PDFExtractorTestRunner:
    """Ejecutor de tests con generación de reportes"""
    
    def __init__(self, output_dir: Path = None):
        """
        Inicializa el ejecutor de tests
        
        Args:
            output_dir: Directorio para guardar resultados
        """
        self.output_dir = output_dir or Path(__file__).parent / "test_results"
        self.output_dir.mkdir(exist_ok=True)
        self.pdf_dir = Path(__file__).parent.parent / "pdfs"
        self.results = {
            'fecha_ejecucion': datetime.now().isoformat(),
            'pdfs_procesados': [],
            'validaciones': [],
            'resumen': {}
        }
    
    def get_pdf_files(self) -> List[Path]:
        """Obtiene todos los archivos PDF disponibles"""
        return sorted(self.pdf_dir.glob("*.pdf"))
    
    def test_init_extractor(self, pdf_path: Path) -> Dict[str, Any]:
        """Test 1: Inicializar PDFExtractor y cargar PDF"""
        test = {
            'nombre': 'Inicialización del Extractor',
            'pdf': pdf_path.name,
            'estado': 'PASS',
            'detalles': '',
            'excepciones': []
        }
        
        try:
            extractor = PDFExtractor(pdf_path)
            test['detalles'] = f"✓ PDF cargado correctamente"
            test['validaciones'] = {
                'reader_valido': extractor.reader is not None,
                'pdf_path_correcto': extractor.pdf_path == pdf_path
            }
        except Exception as e:
            test['estado'] = 'FAIL'
            test['excepciones'].append(str(e))
        
        return test, extractor if test['estado'] == 'PASS' else None
    
    def test_metadata_extraction(self, extractor: PDFExtractor, pdf_path: Path) -> Dict[str, Any]:
        """Test 2: Extracción de metadatos"""
        test = {
            'nombre': 'Extracción de Metadatos',
            'pdf': pdf_path.name,
            'estado': 'PASS',
            'detalles': '',
            'excepciones': []
        }
        
        try:
            metadata = extractor.extract_metadata()
            
            # Validaciones
            validaciones = {
                'es_dict': isinstance(metadata, dict),
                'tiene_claves_requeridas': all(k in metadata for k in ['titulo', 'autor', 'fecha_creacion']),
                'titulo': metadata.get('titulo'),
                'autor': metadata.get('autor'),
                'fecha_creacion': metadata.get('fecha_creacion')
            }
            
            test['validaciones'] = validaciones
            test['detalles'] = f"✓ Metadatos extraídos: {len(metadata)} campos"
            
        except Exception as e:
            test['estado'] = 'FAIL'
            test['excepciones'].append(str(e))
        
        return test, metadata if test['estado'] == 'PASS' else None
    
    def test_page_count(self, extractor: PDFExtractor, pdf_path: Path) -> Dict[str, Any]:
        """Test 3: Obtención del número de páginas"""
        test = {
            'nombre': 'Número de Páginas',
            'pdf': pdf_path.name,
            'estado': 'PASS',
            'detalles': '',
            'excepciones': []
        }
        
        try:
            num_pages = extractor.get_num_pages()
            
            validaciones = {
                'es_int': isinstance(num_pages, int),
                'mayor_que_cero': num_pages > 0,
                'cantidad': num_pages
            }
            
            test['validaciones'] = validaciones
            test['detalles'] = f"✓ PDF contiene {num_pages} páginas"
            
        except Exception as e:
            test['estado'] = 'FAIL'
            test['excepciones'].append(str(e))
        
        return test, num_pages if test['estado'] == 'PASS' else None
    
    def test_text_extraction_single_page(self, extractor: PDFExtractor, pdf_path: Path) -> Dict[str, Any]:
        """Test 4: Extracción de texto de una página"""
        test = {
            'nombre': 'Extracción de Texto - Primera Página',
            'pdf': pdf_path.name,
            'estado': 'PASS',
            'detalles': '',
            'excepciones': []
        }
        
        try:
            text = extractor.extract_text_from_page(0)
            
            validaciones = {
                'es_string': isinstance(text, str),
                'no_vacio': len(text) > 0,
                'longitud_caracteres': len(text),
                'primer_100_chars': text[:100] if len(text) > 0 else ''
            }
            
            test['validaciones'] = validaciones
            test['detalles'] = f"✓ Texto extraído: {len(text)} caracteres"
            
        except Exception as e:
            test['estado'] = 'FAIL'
            test['excepciones'].append(str(e))
        
        return test
    
    def test_all_pages_extraction(self, extractor: PDFExtractor, pdf_path: Path) -> Dict[str, Any]:
        """Test 5: Extracción de todas las páginas"""
        test = {
            'nombre': 'Extracción de Todas las Páginas',
            'pdf': pdf_path.name,
            'estado': 'PASS',
            'detalles': '',
            'excepciones': []
        }
        
        try:
            pages = extractor.extract_all_pages()
            
            validaciones = {
                'es_lista': isinstance(pages, list),
                'cantidad_paginas': len(pages),
                'tiene_estructura': all('numero_pagina' in p and 'contenido' in p for p in pages),
                'numeracion_correcta': all(p['numero_pagina'] == i + 1 for i, p in enumerate(pages))
            }
            
            test['validaciones'] = validaciones
            test['detalles'] = f"✓ {len(pages)} páginas extraídas correctamente"
            
        except Exception as e:
            test['estado'] = 'FAIL'
            test['excepciones'].append(str(e))
        
        return test, pages if test['estado'] == 'PASS' else None
    
    def test_full_document_extraction(self, extractor: PDFExtractor, pdf_path: Path) -> Dict[str, Any]:
        """Test 6: Extracción completa del documento"""
        test = {
            'nombre': 'Extracción Completa del Documento',
            'pdf': pdf_path.name,
            'estado': 'PASS',
            'detalles': '',
            'excepciones': []
        }
        
        try:
            doc = extractor.extract_full_document()
            
            expected_keys = {
                'nombre_archivo', 'ruta_archivo', 'num_paginas',
                'titulo', 'autor', 'fecha_creacion', 'paginas'
            }
            
            validaciones = {
                'es_dict': isinstance(doc, dict),
                'tiene_todas_claves': all(k in doc for k in expected_keys),
                'tipos_correctos': {
                    'nombre_archivo': isinstance(doc.get('nombre_archivo'), str),
                    'ruta_archivo': isinstance(doc.get('ruta_archivo'), str),
                    'num_paginas': isinstance(doc.get('num_paginas'), int),
                    'paginas': isinstance(doc.get('paginas'), list)
                }
            }
            
            test['validaciones'] = validaciones
            test['detalles'] = f"✓ Documento completo extraído: {doc['num_paginas']} páginas"
            
        except Exception as e:
            test['estado'] = 'FAIL'
            test['excepciones'].append(str(e))
        
        return test, doc if test['estado'] == 'PASS' else None
    
    def test_helper_function(self, pdf_path: Path) -> Dict[str, Any]:
        """Test 7: Función auxiliar extract_pdf"""
        test = {
            'nombre': 'Función Auxiliar extract_pdf',
            'pdf': pdf_path.name,
            'estado': 'PASS',
            'detalles': '',
            'excepciones': []
        }
        
        try:
            result = extract_pdf(pdf_path)
            
            validaciones = {
                'es_dict': isinstance(result, dict),
                'tiene_estructura': all(k in result for k in ['nombre_archivo', 'paginas']),
                'nombre_correcto': result.get('nombre_archivo') == pdf_path.name
            }
            
            test['validaciones'] = validaciones
            test['detalles'] = f"✓ Función auxiliar funcionó correctamente"
            
        except Exception as e:
            test['estado'] = 'FAIL'
            test['excepciones'].append(str(e))
        
        return test
    
    def run_all_tests(self):
        """Ejecuta todos los tests en todos los PDFs"""
        pdf_files = self.get_pdf_files()
        
        if not pdf_files:
            print("❌ No se encontraron archivos PDF")
            return
        
        print(f"\n🚀 Iniciando tests para {len(pdf_files)} archivos PDF")
        print("=" * 70)
        
        for pdf_path in pdf_files:
            print(f"\n📄 Procesando: {pdf_path.name}")
            print("-" * 70)
            
            pdf_result = {
                'archivo': pdf_path.name,
                'tests': [],
                'extraccion_completa': None
            }
            
            # Test 1: Inicialización
            test1, extractor = self.test_init_extractor(pdf_path)
            pdf_result['tests'].append(test1)
            print(f"  ✓ {test1['nombre']}: {test1['estado']}")
            
            if not extractor:
                print(f"  ❌ No se pudo continuar con el PDF")
                self.results['pdfs_procesados'].append(pdf_result)
                continue
            
            # Test 2: Metadatos
            test2, metadata = self.test_metadata_extraction(extractor, pdf_path)
            pdf_result['tests'].append(test2)
            print(f"  ✓ {test2['nombre']}: {test2['estado']}")
            
            # Test 3: Número de páginas
            test3, num_pages = self.test_page_count(extractor, pdf_path)
            pdf_result['tests'].append(test3)
            print(f"  ✓ {test3['nombre']}: {test3['estado']}")
            
            # Test 4: Texto de una página
            test4 = self.test_text_extraction_single_page(extractor, pdf_path)
            pdf_result['tests'].append(test4)
            print(f"  ✓ {test4['nombre']}: {test4['estado']}")
            
            # Test 5: Todas las páginas
            test5, pages = self.test_all_pages_extraction(extractor, pdf_path)
            pdf_result['tests'].append(test5)
            print(f"  ✓ {test5['nombre']}: {test5['estado']}")
            
            # Test 6: Documento completo
            test6, doc = self.test_full_document_extraction(extractor, pdf_path)
            pdf_result['tests'].append(test6)
            print(f"  ✓ {test6['nombre']}: {test6['estado']}")
            pdf_result['extraccion_completa'] = doc
            
            # Test 7: Función auxiliar
            test7 = self.test_helper_function(pdf_path)
            pdf_result['tests'].append(test7)
            print(f"  ✓ {test7['nombre']}: {test7['estado']}")
            
            self.results['pdfs_procesados'].append(pdf_result)
        
        self._calculate_statistics()
        self._save_results()
    
    def _calculate_statistics(self):
        """Calcula estadísticas de los tests"""
        total_tests = 0
        passed_tests = 0
        failed_tests = 0
        
        for pdf_result in self.results['pdfs_procesados']:
            for test in pdf_result['tests']:
                total_tests += 1
                if test['estado'] == 'PASS':
                    passed_tests += 1
                else:
                    failed_tests += 1
        
        self.results['resumen'] = {
            'total_pdfs': len(self.results['pdfs_procesados']),
            'total_tests': total_tests,
            'tests_pasados': passed_tests,
            'tests_fallidos': failed_tests,
            'tasa_exito': f"{(passed_tests/total_tests*100):.2f}%" if total_tests > 0 else "0%"
        }
    
    def _save_results(self):
        """Guarda los resultados en archivos JSON"""
        # Guardar resumen general
        summary_file = self.output_dir / "test_summary.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)
        print(f"\n✓ Resumen guardado en: {summary_file}")
        
        # Guardar extracción completa de cada PDF
        for pdf_result in self.results['pdfs_procesados']:
            if pdf_result['extraccion_completa']:
                filename = pdf_result['archivo'].replace('.pdf', '_extraction.json')
                filepath = self.output_dir / filename
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(pdf_result['extraccion_completa'], f, ensure_ascii=False, indent=2)
                print(f"✓ Extracción guardada en: {filepath}")
        
        # Guardar detalle de validaciones
        validations_file = self.output_dir / "detailed_validations.json"
        detailed_validations = {
            'fecha': datetime.now().isoformat(),
            'pdfs': []
        }
        
        for pdf_result in self.results['pdfs_procesados']:
            pdf_detail = {
                'archivo': pdf_result['archivo'],
                'tests': pdf_result['tests']
            }
            detailed_validations['pdfs'].append(pdf_detail)
        
        with open(validations_file, 'w', encoding='utf-8') as f:
            json.dump(detailed_validations, f, ensure_ascii=False, indent=2)
        print(f"✓ Validaciones detalladas guardadas en: {validations_file}")
    
    def print_summary(self):
        """Imprime un resumen de los resultados"""
        print("\n" + "=" * 70)
        print("📊 RESUMEN DE TESTS")
        print("=" * 70)
        summary = self.results['resumen']
        print(f"Total de PDFs procesados: {summary['total_pdfs']}")
        print(f"Total de tests realizados: {summary['total_tests']}")
        print(f"Tests pasados: {summary['tests_pasados']} ✓")
        print(f"Tests fallidos: {summary['tests_fallidos']} ✗")
        print(f"Tasa de éxito: {summary['tasa_exito']}")
        print("=" * 70 + "\n")


def main():
    """Función principal"""
    runner = PDFExtractorTestRunner()
    runner.run_all_tests()
    runner.print_summary()


if __name__ == "__main__":
    main()
