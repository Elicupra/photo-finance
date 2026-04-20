from __future__ import annotations

import importlib
from pathlib import Path

import pytest

from backend.components import parse_pdf_text
from backend.components.extract_pdf import extract_pdf
from backend.components.text_to_json import text_to_json


REPO_ROOT = Path(__file__).resolve().parents[2]
PDF_PATH = REPO_ROOT / 'backend' / 'container_pdf' / 'Naturgy_01_25.pdf'


def test_find_pdf_file():
    assert PDF_PATH.exists(), f'PDF de prueba no encontrado: {PDF_PATH}'
    assert PDF_PATH.suffix.lower() == '.pdf'


def test_read_pdf_file_from_disk():
    pdf_bytes = PDF_PATH.read_bytes()

    assert pdf_bytes
    assert pdf_bytes.startswith(b'%PDF')


def test_extract_structured_data_from_text_with_current_helpers():
    raw_text = 'FACTURA electricidad TOTAL A PAGAR: 123,45 EUR'

    cleaned_text = parse_pdf_text.limpiar_texto(raw_text)
    debt = parse_pdf_text.parse_invoice_debt(cleaned_text)
    concept = parse_pdf_text.find_concepts_keys(cleaned_text)

    assert cleaned_text == raw_text
    assert debt == pytest.approx(123.45)
    assert concept == 'electricidad'


def test_extract_pdf_with_easyocr_works_after_fix():
    """Test that extract_pdf now works with EasyOCR after converting PIL to numpy array"""
    result = extract_pdf(str(PDF_PATH), use_tesseract=False)
    
    # Should return non-empty string with EasyOCR
    assert isinstance(result, str)
    assert len(result) > 0
    # Should contain page markers
    assert '---' in result


def test_extract_pdf_with_tesseract_ocr_works():
    """Test that extract_pdf works when using Tesseract OCR"""
    result = extract_pdf(str(PDF_PATH), use_tesseract=True)
    
    # Should return non-empty string with Tesseract
    assert isinstance(result, str)
    assert len(result) > 0
    # Should contain page markers
    assert '---' in result


def test_backend_main_currently_fails_to_import():
    with pytest.raises(ModuleNotFoundError, match="No module named 'components'"):
        importlib.import_module('backend.main')


def test_text_to_json_currently_returns_builtin_type_instead_of_invoice_type():
    structured = text_to_json('electricidad', 123.45, 'suministro')

    assert structured['concepto'] == 'electricidad'
    assert structured['deuda'] == pytest.approx(123.45)
    assert structured['tipo_factura'] is type

#Test para validar lectura de PDF. Se vuelca el resultado en un fichero plano txt
# El fichero plano se guardara en test/prueba_raw.txt
def test_extract_pdf_and_save_to_txt():
    pdf_path = PDF_PATH
    extracted_text = extract_pdf(str(pdf_path), use_tesseract=False)
    
    # Guardar el texto extraído en un archivo plano
    output_txt_path = REPO_ROOT / 'tests' / 'prueba_raw.txt'
    with open(output_txt_path, 'w', encoding='utf-8') as f:
        f.write(extracted_text)
    
    # Verificar que el archivo se ha creado y contiene texto
    assert output_txt_path.exists(), f'Archivo de salida no encontrado: {output_txt_path}'
    assert output_txt_path.stat().st_size > 0, 'El archivo de salida está vacío'