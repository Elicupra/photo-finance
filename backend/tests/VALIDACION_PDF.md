# Validacion unificada del pipeline PDF

Fecha de ejecucion: 2026-04-20

Comando ejecutado:

```powershell
d:/GitHub/photo-finance/.venv/Scripts/python.exe -m pytest backend/tests/test_pdf_pipeline_validation.py -v
```

Resultado global:

- Total: 8 tests
- OK: 7
- KO: 1
- Warnings: 10
- Duracion: 190.09s

## Detalle de validaciones

| Caso validado | Estado | Evidencia |
| --- | --- | --- |
| Encontrar PDF de prueba (`Naturgy_01_25.pdf`) | OK | `test_find_pdf_file` pasa |
| Lectura binaria del PDF y cabecera `%PDF` | OK | `test_read_pdf_file_from_disk` pasa |
| Extraccion de datos estructurados del texto (helpers actuales) | OK | `test_extract_structured_data_from_text_with_current_helpers` pasa |
| OCR con EasyOCR | OK | `test_extract_pdf_with_easyocr_works_after_fix` pasa |
| OCR con Tesseract OCR | OK | `test_extract_pdf_with_tesseract_ocr_works` pasa |
| Comprobacion de import del backend | OK (como validacion de fallo esperado) | `test_backend_main_currently_fails_to_import` pasa esperando `ModuleNotFoundError: No module named 'components'` |
| Validacion de `text_to_json` segun codigo actual | OK (como validacion de bug actual) | `test_text_to_json_currently_returns_builtin_type_instead_of_invoice_type` pasa, confirma que `tipo_factura` devuelve `type` |
| Lectura PDF y volcado a TXT | KO | `test_extract_pdf_and_save_to_txt` falla con `FileNotFoundError` en `D:\GitHub\photo-finance\tests\prueba_raw.txt` |

## KO detectados y causa

### 1) KO en prueba de guardado TXT

- Caso: `test_extract_pdf_and_save_to_txt`
- Error: `FileNotFoundError: [Errno 2] No such file or directory: 'D:\\GitHub\\photo-finance\\tests\\prueba_raw.txt'`
- Causa: la carpeta destino `tests` en raiz no existe en el momento de la prueba.

### 2) Problematica actual del endpoint

Aunque el test de import se marca OK (porque valida el fallo esperado), funcionalmente el endpoint sigue KO por estos motivos:

- `backend/main.py` usa `from components.extract_pdf ...`, lo que provoca `ModuleNotFoundError` al importar desde la raiz del repo.
- En `/process-pdf/`, la firma `file: UploadFile = pdf_path` no es una definicion valida para un archivo subido en FastAPI.
- En `/process-pdf/`, se usa ruta temporal fija `/tmp/...`, no portable en Windows.
- En `/process-text/`, se llama `parse_pdf_text.find_invoice_type(...)`, funcion que no existe en `parse_pdf_text.py`.
- En `/process-text/`, se invoca `text_to_json(cleaned_text, concept, debt, type_invoice)` con numero de argumentos incompatible con la firma actual de `text_to_json`.

## Conclusion

La validacion actual confirma que el OCR (EasyOCR y Tesseract), lectura de PDF y parsing base funcionan. El flujo endpoint completo todavia no esta operativo y queda bloqueado por errores de importacion y de contrato entre funciones.
