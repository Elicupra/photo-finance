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


def test_extract_pdf_currently_fails_with_easyocr_input_type():
    with pytest.raises(ValueError, match='Invalid input type'):
        extract_pdf(str(PDF_PATH), use_tesseract=False)


def test_backend_main_currently_fails_to_import():
    with pytest.raises(ImportError, match="cannot import name 'text_to_json' from 'backend.components.extract_pdf'"):
        importlib.import_module('backend.main')


def test_text_to_json_currently_returns_builtin_type_instead_of_invoice_type():
    structured = text_to_json('electricidad', 123.45, 'suministro')

    assert structured['concepto'] == 'electricidad'
    assert structured['deuda'] == pytest.approx(123.45)
    assert structured['tipo_factura'] is type