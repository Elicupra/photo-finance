from __future__ import annotations

import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from backend.components import parse_pdf_text
from backend.components.extract_pdf import extract_pdf
from backend.components.text_to_json import text_to_json


PDF_PATH = REPO_ROOT / 'backend' / 'container_pdf' / 'Naturgy_01_25.pdf'
OUTPUT_DIR = REPO_ROOT / 'backend' / 'tests' / '_tmp_outputs'
RAW_TEXT_PATH = OUTPUT_DIR / 'pipeline_raw_tesseract.txt'
RESULT_PATH = OUTPUT_DIR / 'pipeline_result_tesseract.json'


def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    result = {
        'pdf_found': False,
        'pdf_readable': False,
        'tesseract_extraction_ok': False,
        'text_cleaning_ok': False,
        'concept_detected': None,
        'debt_detected': None,
        'text_to_json_current_ok': False,
        'notes': [],
    }

    if not PDF_PATH.exists():
        result['notes'].append(f'KO: PDF no encontrado: {PDF_PATH}')
        RESULT_PATH.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding='utf-8')
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 1

    result['pdf_found'] = True

    pdf_bytes = PDF_PATH.read_bytes()
    result['pdf_readable'] = bool(pdf_bytes and pdf_bytes.startswith(b'%PDF'))
    if not result['pdf_readable']:
        result['notes'].append('KO: El archivo existe pero no parece un PDF válido.')

    extracted_text = extract_pdf(str(PDF_PATH), use_tesseract=True)
    RAW_TEXT_PATH.write_text(extracted_text, encoding='utf-8')

    result['tesseract_extraction_ok'] = isinstance(extracted_text, str) and len(extracted_text.strip()) > 0
    if not result['tesseract_extraction_ok']:
        result['notes'].append('KO: Tesseract no devolvió texto útil.')

    cleaned_text = parse_pdf_text.limpiar_texto(extracted_text)
    result['text_cleaning_ok'] = isinstance(cleaned_text, str) and len(cleaned_text) > 0

    concept = parse_pdf_text.find_concepts_keys(cleaned_text)
    debt = parse_pdf_text.parse_invoice_debt(cleaned_text)
    result['concept_detected'] = concept
    result['debt_detected'] = debt

    inferred_type = concept or 'No especificado'
    structured = text_to_json(concept, debt, inferred_type)
    serializable_structured = {
        key: (value.__name__ if isinstance(value, type) else value)
        for key, value in structured.items()
    }

    # Valida el comportamiento real actual de text_to_json.
    result['text_to_json_current_ok'] = structured.get('tipo_factura') == inferred_type
    if not result['text_to_json_current_ok']:
        result['notes'].append(
            'KO: text_to_json no conserva type_invoice; devuelve el builtin type en tipo_factura.'
        )

    RESULT_PATH.write_text(
        json.dumps({'result': result, 'structured': serializable_structured}, indent=2, ensure_ascii=False),
        encoding='utf-8',
    )

    print('Pipeline manual Tesseract')
    print(f'PDF: {PDF_PATH}')
    print(f'Texto OCR: {RAW_TEXT_PATH}')
    print(f'Resultado JSON: {RESULT_PATH}')
    print(json.dumps(result, indent=2, ensure_ascii=False))

    return 0


if __name__ == '__main__':
    raise SystemExit(main())