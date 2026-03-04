"""
Tests para el módulo PDFExtractor
"""
import pytest
from pathlib import Path
import sys

# Agregar el directorio backend al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from extractors.pdf_extractor import PDFExtractor, extract_pdf


class TestPDFExtractor:
    """Tests para la clase PDFExtractor"""
    
    @pytest.fixture
    def pdf_path(self):
        """Fixture que proporciona la ruta a un PDF de prueba"""
        return Path(__file__).parent.parent / "pdfs" / "Naturgy_01_25.pdf"
    
    @pytest.fixture
    def extractor(self, pdf_path):
        """Fixture que proporciona una instancia de PDFExtractor"""
        return PDFExtractor(pdf_path)
    
    # ==================== Tests de Inicialización ====================
    
    def test_init_con_ruta_valida(self, pdf_path):
        """Test: Inicializar PDFExtractor con ruta válida"""
        extractor = PDFExtractor(pdf_path)
        assert extractor.pdf_path == pdf_path
        assert extractor.reader is not None
    
    def test_init_con_string_path(self):
        """Test: Inicializar PDFExtractor con string en lugar de Path"""
        pdf_path = str(Path(__file__).parent.parent / "pdfs" / "Naturgy_01_25.pdf")
        extractor = PDFExtractor(pdf_path)
        assert extractor.reader is not None
    
    def test_init_con_ruta_invalida(self):
        """Test: Inicializar PDFExtractor con ruta inexistente"""
        with pytest.raises(ValueError, match="Error al cargar el PDF"):
            PDFExtractor(Path(__file__).parent / "inexistente.pdf")
    
    # ==================== Tests de Metadatos ====================
    
    def test_extract_metadata_retorna_dict(self, extractor):
        """Test: extract_metadata retorna un diccionario"""
        metadata = extractor.extract_metadata()
        assert isinstance(metadata, dict)
        assert 'titulo' in metadata
        assert 'autor' in metadata
        assert 'fecha_creacion' in metadata
    
    def test_extract_metadata_estructura(self, extractor):
        """Test: extract_metadata tiene la estructura esperada"""
        metadata = extractor.extract_metadata()
        assert len(metadata) == 3
        # Los valores pueden ser None o string
        assert metadata['titulo'] is None or isinstance(metadata['titulo'], str)
        assert metadata['autor'] is None or isinstance(metadata['autor'], str)
        assert metadata['fecha_creacion'] is None or metadata['fecha_creacion'] is not None
    
    # ==================== Tests de Número de Páginas ====================
    
    def test_get_num_pages_retorna_int(self, extractor):
        """Test: get_num_pages retorna un entero"""
        num_pages = extractor.get_num_pages()
        assert isinstance(num_pages, int)
        assert num_pages > 0
    
    def test_get_num_pages_valor_positivo(self, extractor):
        """Test: get_num_pages retorna un valor positivo"""
        num_pages = extractor.get_num_pages()
        assert num_pages >= 1
    
    # ==================== Tests de Extracción de Texto ====================
    
    def test_extract_text_from_page_primera_pagina(self, extractor):
        """Test: Extraer texto de la primera página"""
        text = extractor.extract_text_from_page(0)
        assert isinstance(text, str)
    
    def test_extract_text_from_page_retorna_string(self, extractor):
        """Test: extract_text_from_page retorna un string"""
        num_pages = extractor.get_num_pages()
        if num_pages > 0:
            text = extractor.extract_text_from_page(0)
            assert isinstance(text, str)
    
    def test_extract_text_from_page_indice_invalido(self, extractor):
        """Test: extract_text_from_page con índice fuera de rango retorna string vacío"""
        num_pages = extractor.get_num_pages()
        text = extractor.extract_text_from_page(num_pages + 100)
        assert isinstance(text, str)
        assert text == ""
    
    def test_extract_text_from_page_negativo(self, extractor):
        """Test: extract_text_from_page con índice negativo"""
        text = extractor.extract_text_from_page(-1)
        assert isinstance(text, str)
    
    # ==================== Tests de Extracción de Todas las Páginas ====================
    
    def test_extract_all_pages_retorna_list(self, extractor):
        """Test: extract_all_pages retorna una lista"""
        pages = extractor.extract_all_pages()
        assert isinstance(pages, list)
    
    def test_extract_all_pages_estructura(self, extractor):
        """Test: extract_all_pages retorna estructura correcta"""
        pages = extractor.extract_all_pages()
        assert len(pages) > 0
        
        for page in pages:
            assert isinstance(page, dict)
            assert 'numero_pagina' in page
            assert 'contenido' in page
            assert isinstance(page['numero_pagina'], int)
            assert isinstance(page['contenido'], str)
    
    def test_extract_all_pages_numeracion_correcta(self, extractor):
        """Test: extract_all_pages tiene numeración 1-indexed correcta"""
        pages = extractor.extract_all_pages()
        num_pages = extractor.get_num_pages()
        
        assert len(pages) == num_pages
        for i, page in enumerate(pages):
            assert page['numero_pagina'] == i + 1  # Debe ser 1-indexed
    
    # ==================== Tests de Extracción Completa ====================
    
    def test_extract_full_document_retorna_dict(self, extractor):
        """Test: extract_full_document retorna un diccionario"""
        doc = extractor.extract_full_document()
        assert isinstance(doc, dict)
    
    def test_extract_full_document_estructura_completa(self, extractor):
        """Test: extract_full_document tiene todas las claves esperadas"""
        doc = extractor.extract_full_document()
        
        expected_keys = {
            'nombre_archivo',
            'ruta_archivo',
            'num_paginas',
            'titulo',
            'autor',
            'fecha_creacion',
            'paginas'
        }
        
        assert all(key in doc for key in expected_keys)
    
    def test_extract_full_document_tipos_valores(self, extractor):
        """Test: extract_full_document tiene tipos de valores correctos"""
        doc = extractor.extract_full_document()
        
        assert isinstance(doc['nombre_archivo'], str)
        assert isinstance(doc['ruta_archivo'], str)
        assert isinstance(doc['num_paginas'], int)
        assert doc['titulo'] is None or isinstance(doc['titulo'], str)
        assert doc['autor'] is None or isinstance(doc['autor'], str)
        assert isinstance(doc['paginas'], list)
    
    def test_extract_full_document_num_paginas_consistente(self, extractor):
        """Test: num_paginas en extract_full_document es consistente con get_num_pages"""
        doc = extractor.extract_full_document()
        assert doc['num_paginas'] == extractor.get_num_pages()
    
    def test_extract_full_document_paginas_consistente(self, extractor):
        """Test: paginas en extract_full_document es consistente con extract_all_pages"""
        doc = extractor.extract_full_document()
        expected_pages = extractor.extract_all_pages()
        assert len(doc['paginas']) == len(expected_pages)
    
    # ==================== Tests de Función Auxiliar ====================
    
    def test_extract_pdf_function(self, pdf_path):
        """Test: Función extract_pdf funciona correctamente"""
        result = extract_pdf(pdf_path)
        
        assert isinstance(result, dict)
        assert 'nombre_archivo' in result
        assert 'paginas' in result
        assert isinstance(result['paginas'], list)
    
    def test_extract_pdf_function_equivalente_a_extract_full_document(self, pdf_path):
        """Test: extract_pdf produce el mismo resultado que PDFExtractor.extract_full_document"""
        result1 = extract_pdf(pdf_path)
        extractor = PDFExtractor(pdf_path)
        result2 = extractor.extract_full_document()
        
        # Comparar claves y estructura
        assert result1.keys() == result2.keys()
        assert result1['num_paginas'] == result2['num_paginas']
        assert len(result1['paginas']) == len(result2['paginas'])


class TestPDFExtractorMultipleFiles:
    """Tests con múltiples archivos PDF"""
    
    @pytest.fixture
    def pdf_files(self):
        """Fixture que proporciona todas las rutas de PDFs disponibles"""
        pdf_dir = Path(__file__).parent.parent / "pdfs"
        return sorted(pdf_dir.glob("*.pdf"))
    
    def test_todos_los_pdfs_pueden_cargarse(self, pdf_files):
        """Test: Todos los PDFs pueden cargarse sin error"""
        assert len(pdf_files) > 0, "No se encontraron archivos PDF"
        
        for pdf_file in pdf_files:
            extractor = PDFExtractor(pdf_file)
            assert extractor.reader is not None
    
    def test_todos_los_pdfs_tienen_metadatos(self, pdf_files):
        """Test: Todos los PDFs pueden extraer metadatos"""
        for pdf_file in pdf_files:
            extractor = PDFExtractor(pdf_file)
            metadata = extractor.extract_metadata()
            assert isinstance(metadata, dict)
    
    def test_todos_los_pdfs_tienen_paginas(self, pdf_files):
        """Test: Todos los PDFs tienen al menos una página"""
        for pdf_file in pdf_files:
            extractor = PDFExtractor(pdf_file)
            num_pages = extractor.get_num_pages()
            assert num_pages >= 1
    
    def test_extraccion_completa_todos_pdfs(self, pdf_files):
        """Test: Extracción completa funciona en todos los PDFs"""
        assert len(pdf_files) > 0
        
        for pdf_file in pdf_files:
            extractor = PDFExtractor(pdf_file)
            doc = extractor.extract_full_document()
            
            # Validaciones básicas
            assert doc['nombre_archivo'] == pdf_file.name
            assert doc['num_paginas'] > 0
            assert len(doc['paginas']) == doc['num_paginas']
            
            # Cada página debe tener contenido
            for page in doc['paginas']:
                assert page['numero_pagina'] >= 1
                assert isinstance(page['contenido'], str)


class TestPDFExtractorEdgeCases:
    """Tests para casos límite y errores"""
    
    def test_load_pdf_con_archivo_corrupto(self, tmp_path):
        """Test: Manejo de archivo PDF corrupto"""
        # Crear un archivo con contenido inválido
        fake_pdf = tmp_path / "fake.pdf"
        fake_pdf.write_text("Este no es un PDF válido")
        
        with pytest.raises(ValueError, match="Error al cargar el PDF"):
            PDFExtractor(fake_pdf)
    
    def test_extract_metadata_sin_metadatos(self):
        """Test: PDF sin metadatos retorna valores None"""
        # Los PDFs de prueba pueden no tener metadatos
        pdf_path = Path(__file__).parent.parent / "pdfs" / "Naturgy_01_25.pdf"
        extractor = PDFExtractor(pdf_path)
        metadata = extractor.extract_metadata()
        
        # Si no hay metadatos, los valores deberían ser None
        # Si hay, deberían ser strings
        assert all(
            v is None or isinstance(v, (str, type(None)))
            for v in metadata.values()
        )


# ==================== Tests de Integración ====================

class TestPDFExtractorIntegration:
    """Tests de integración del flujo completo"""
    
    def test_flujo_completo_extraccion(self):
        """Test: Flujo completo de extracción de un PDF"""
        pdf_path = Path(__file__).parent.parent / "pdfs" / "Naturgy_01_25.pdf"
        
        # 1. Crear extractor
        extractor = PDFExtractor(pdf_path)
        
        # 2. Obtener número de páginas
        num_pages = extractor.get_num_pages()
        assert num_pages > 0
        
        # 3. Extraer metadatos
        metadata = extractor.extract_metadata()
        assert isinstance(metadata, dict)
        
        # 4. Extraer texto de primera página
        text = extractor.extract_text_from_page(0)
        assert isinstance(text, str)
        
        # 5. Extraer todas las páginas
        pages = extractor.extract_all_pages()
        assert len(pages) == num_pages
        
        # 6. Extraer documento completo
        doc = extractor.extract_full_document()
        assert doc['num_paginas'] == num_pages
        assert len(doc['paginas']) == num_pages
    
    def test_flujo_con_funcion_auxiliar(self):
        """Test: Flujo usando la función auxiliar extract_pdf"""
        pdf_path = Path(__file__).parent.parent / "pdfs" / "Naturgy_01_25.pdf"
        
        result = extract_pdf(pdf_path)
        
        # Validaciones
        assert result['nombre_archivo'] == pdf_path.name
        assert result['num_paginas'] > 0
        assert len(result['paginas']) == result['num_paginas']
        assert all('numero_pagina' in p and 'contenido' in p for p in result['paginas'])


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
