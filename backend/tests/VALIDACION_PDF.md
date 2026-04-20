# Validacion actual del pipeline PDF

## Alcance

Se ha creado una suite dedicada en `backend/tests/test_pdf_pipeline_validation.py` para validar el flujo actual del backend sin usar `backend/test.py`.

Comando ejecutado:

```powershell
d:/GitHub/photo-finance/.venv/Scripts/python.exe -m pytest backend/tests/test_pdf_pipeline_validation.py -vv
```

Resultado de la ejecucion:

- `6 passed`
- `4 warnings` de dependencias `easyocr/torch`
- Tiempo aproximado: `6.59s`

## Pruebas realizadas

| Caso | Estado | Validacion realizada | Resultado real |
| --- | --- | --- | --- |
| Encontrar PDF | OK | Se comprueba la existencia de `backend/container_pdf/Naturgy_01_25.pdf` | El fichero existe y tiene extension `.pdf` |
| Lectura de PDF | OK | Se abre el fichero en binario y se valida la cabecera `%PDF` | El PDF se puede leer desde disco correctamente |
| Extraccion de datos segun el codigo actual | KO | Se ejecuta `backend.components.extract_pdf.extract_pdf(..., use_tesseract=False)` sobre un PDF real | Falla con `ValueError: Invalid input type. Supporting format = string(file path or url), bytes, numpy array` porque se pasan imagenes PIL directamente a `easyocr.Reader.readtext()` |
| Parsing estructurado disponible hoy | OK | Se valida `limpiar_texto`, `parse_invoice_debt` y `find_concepts_keys` con texto representativo | El parser actual extrae `123.45` y detecta `electricidad` |
| Devolucion del PDF por backend | KO | Se intenta importar `backend.main` para poder probar el endpoint `/process-pdf/` | No se puede probar el endpoint porque `backend.main` falla al importar con `ImportError: cannot import name 'text_to_json' from 'backend.components.extract_pdf'` |
| Estructuracion JSON final | KO | Se valida `backend.components.text_to_json.text_to_json()` | La clave `tipo_factura` devuelve el builtin `type` en lugar del valor recibido |

## Conclusion

El estado actual del backend permite:

- localizar PDFs reales de prueba
- leer el fichero PDF desde disco
- ejecutar correctamente parte del parser textual

El estado actual del backend no permite completar el flujo extremo a extremo de OCR y respuesta FastAPI por estos motivos:

1. `extract_pdf()` rompe al invocar EasyOCR con un tipo de dato no soportado.
2. `backend.main` no importa correctamente, por lo que el endpoint `/process-pdf/` no puede probarse de forma real.
3. `text_to_json()` no devuelve el `type_invoice` recibido.

## Nota sobre la suite

La suite pasa porque valida el comportamiento observable actual, incluyendo los fallos esperados (`KO`) para dejar evidencia reproducible del estado del sistema a fecha de esta ejecucion.