# Guía de Instalación y Uso: Extracción Genérica de Facturas

## ✅ Estado Actual

Se ha implementado un sistema de **extracción genérica de conceptos** que:

✓ Extrae **metadatos** (empresa, número de factura, cliente, fechas)
✓ Identifica **conceptos/servicios** sin depender del formato específico
✓ Captura **importes** (total, IVA, subtotal, etc.) automáticamente
✓ Funciona con múltiples tipos de facturas (Naturgy, DIGI, etc.)
✓ Soporta **EasyOCR** por defecto
✓ Soporta **Tesseract OCR** como opción más precisa

---

## 📋 Estructura de Datos

La función `parse_invoice()` retorna:

```json
{
  "metadatos": {
    "empresa": "DIGI",
    "numero_factura": "DGFC2514370141",
    "cliente_nombre": "Eliseo Ortigosa Guerrero",
    "numero_contrato": "23214492",
    "numero_cliente": "11495672",
    ...
  },
  "fechas": {
    "emision": "23/06/2025",
    "vencimiento": "27/06/2025",
    "periodo_desde": "16/05/2025",
    "periodo_hasta": "15/06/2025"
  },
  "conceptos": [
    {
      "descripcion": "Fibra SMART 1Gb",
      "valor": 20.00,
      "tipo": "servicio",
      "linea": 44
    },
    ...
  ],
  "importes": {
    "total_a_pagar": 25.80,
    "subtotal": 21.53,
    "iva": 4.52
  },
  "consumos": []
}
```

---

## 🔧 Instalación de Tesseract (Opcional)

Tesseract es más preciso que EasyOCR pero requiere instalación del motor.

### En Windows:

1. Descargar el instalador desde: https://github.com/UB-Mannheim/tesseract/wiki
   
```bash
# Instalar el paquete Python
pip install pytesseract
```

2. Luego en test.py, cambiar:
```python
texto_extraido = extract_pdf(pdf_path, use_tesseract=True)
```

### En Linux/Mac:

```bash
# Ubuntu/Debian
sudo apt-get install tesseract-ocr

# macOS
brew install tesseract

# Python
pip install pytesseract
```

---

## 🚀 Uso

### Con EasyOCR (por defecto):
```python
from test import extract_pdf, parse_invoice

# Extrae texto
texto = extract_pdf("ruta/al/pdf.pdf")

# Procesa conceptos
factura = parse_invoice(texto)

# Acceder a datos
print(factura["metadatos"]["numero_factura"])
print(factura["importes"]["total_a_pagar"])
```

### Con Tesseract OCR:
```python
from test import extract_pdf, parse_invoice

# Usa Tesseract si está disponible
texto = extract_pdf("ruta/al/pdf.pdf", use_tesseract=True)
factura = parse_invoice(texto)
```

---

## 📊 Ventajas del Enfoque Genérico

| Aspecto | Antes | Ahora |
|--------|-------|-------|
| **Formato** | Solo Naturgy | Múltiples empresas |
| **Conceptos** | Limitados | Cualquier servicio |
| **Flexibilidad** | Rígida | Adaptativa |
| **Mantenimiento** | Alto | Bajo |

---

## 🎯 Comparativa: EasyOCR vs Tesseract

| Criterio | EasyOCR | Tesseract |
|----------|---------|-----------|
| Velocidad | Lenta (~30-60s) | Rápida (~5-10s) |
| Precisión | Buena | Excelente |
| Instalación | Fácil (pip) | Compleja |
| GPU Support | Sí | No |
| Memoria | Media | Baja |
| Idiomas | Múltiples | Múltiples |

**Recomendación**: Usar **Tesseract** para producción si la instalación es factible.

---

## 📝 Próximos Pasos

1. **Integración con Frontend Angular**:
   - Endpoint POST `/api/facturas/procesar`
   - Retorna JSON estructurado

2. **Base de Datos**:
   - Guardar facturas procesadas
   - Historial de cliente

3. **Mejoras**:
   - Machine Learning para clasificar conceptos
   - Validación de importes
   - Detección de anomalías

---

## 🔍 Debugging

Para ver qué se está extrayendo:

```python
import json
from test import extract_pdf, parse_invoice

texto = extract_pdf("pdf_path")
factura = parse_invoice(texto)

# Ver todo en formato JSON
print(json.dumps(factura, indent=2, ensure_ascii=False))

# Ver solo metadatos
print(factura["metadatos"])

# Ver todos los servicios
for servicio in factura["conceptos"]:
    print(f"{servicio['descripcion']}: {servicio['valor']}€")
```

---

## ⚠️ Limitaciones Actuales

- Texto extraído mediante OCR puede tener errores
- Algunos formatos de factura aún no capturados perfectamente
- Consumos (electricidad por tipo) se extraen solo de ciertos formatos
- Se recomienda validación manual para importes altos

---

**Última actualización**: 10/03/2026
