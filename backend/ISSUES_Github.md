# Issues GitHub - Photo Finance MVP

> Copiar y pegar cada sección para crear una issue en GitHub

---

## Issue 1: Crear servicio InvoiceService en Angular con HttpClient

**Título:**
```
1. Crear servicio InvoiceService en Angular con HttpClient
```

**Cuerpo:**
```
## Descripción
Crear un servicio Angular para comunicación con el backend de procesamiento de facturas.

## Tareas
- [ ] Crear `src/app/services/invoice.service.ts`
- [ ] Implementar método `processPdf(file: File)` que envíe FormData al endpoint `/process-pdf/`
- [ ] Implementar método `processText(text: string)` que envíe JSON al endpoint `/process-text/`
- [ ] Usar `HttpClient` de Angular

## Endpoints del backend
- `POST http://localhost:8000/process-pdf/` - Envía PDF, retorna texto extraído
- `POST http://localhost:8000/process-text/` - Envía texto, retorna JSON con concepto, deuda, tipo_factura

## Respuesta esperada del backend
```json
{
  "status": "success",
  "structured_data": {
    "concepto": "Luz",
    "deuda": 56.87,
    "tipo_factura": "Luz"
  }
}
```
```

---

## Issue 2: Integrar InvoiceService en UploadInvoiceComponent

**Título:**
```
2. Integrar InvoiceService en UploadInvoiceComponent
```

**Cuerpo:**
```
## Descripción
Actualizar el componente `UploadInvoiceComponent` para que llame al servicio al guardar el archivo.

## Contexto
El componente actualmente solo previsualiza el archivo sin enviarlo al backend. Ver: `src/app/component/upload-invoice.component/upload-invoice.component.ts:41-46`

## Tareas
- [ ] Importar `InvoiceService` en el componente
- [ ] Inyectar el servicio en el constructor
- [ ] Modificar el método `save()` para llamar a `invoiceService.processPdf(file)`
- [ ] Manejar la respuesta y navegar a la pantalla de resumen
- [ ] Agregar manejo de errores (mostrar mensaje al usuario)

## Ejemplo de implementación
```typescript
save() {
  if (this.invoiceFile) {
    this.invoiceService.processPdf(this.invoiceFile).subscribe({
      next: (response) => {
        console.log('PDF procesado:', response);
        // TODO: Navegar a pantalla de resumen con los datos
      },
      error: (err) => console.error('Error:', err)
    });
  }
}
```
```

---

## Issue 3: Habilitar HttpClient en app.config.ts

**Título:**
```
3. Habilitar HttpClient en app.config.ts
```

**Cuerpo:**
```
## Descripción
Configurar Angular para usar HttpClient, requerido para las llamadas HTTP.

## Tareas
- [ ] Importar `provideHttpClient` en `src/app/app.config.ts`
- [ ] Agregar `provideHttpClient()` al array de providers

## Ejemplo
```typescript
import { provideHttpClient } from '@angular/common/http';

export const appConfig: ApplicationConfig = {
  providers: [
    provideHttpClient(),
    // ... otros providers
  ]
};
```
```

---

## Issue 4: Corregir routes.py - errores de importación

**Título:**
```
4. Corregir routes.py - errores de importación
```

**Cuerpo:**
```
## Descripción
El archivo `routes.py` tiene errores que impiden su uso:
1. Usa `Depends(get_db)` pero no importa la función
2. Usa `settings` pero `config.py` está vacío

## Ubicación
`backend/routes.py`

## Errores actuales
```python
# Línea 5: falta importar Depends
from fastapi import APIRouter, UploadFile, File, HTTPException  # ← Falta Depends
from sqlalchemy.orm import Session

# Línea 21: settings no existe
file_location = f"{settings.FILE_PDF_PATH}/{file.filename}"  # ← settings no está definido
```

## Tareas
- [ ] Opción A: Corregir las importaciones y completar config.py
- [ ] Opción B: Eliminar routes.py y no usarlo (los endpoints ya existen en app.py)

## Recomendación
Se recomienda la Opción B ya que los endpoints principales ya están definidos en `app.py`.
```

---

## Issue 5: Completar config.py con settings

**Título:**
```
5. Completar config.py con settings
```

**Cuerpo:**
```
## Descripción
El archivo `config.py` está vacío pero es referenciado por `models.py`.

## Ubicación
`backend/config.py`

## Tareas
- [ ] Crear clase de configuración con pydantic-settings
- [ ] Definir variables: DATABASE_URL, FILE_PDF_PATH, CORS_ORIGINS, BACKEND_HOST, BACKEND_PORT

## Ejemplo
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./photo_finance.db"
    FILE_PDF_PATH: str = "./container_pdf"
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:4200"
    BACKEND_HOST: str = "0.0.0.0"
    BACKEND_PORT: int = 8000

settings = Settings()
```
```

---

## Issue 6: Crear requirements.txt

**Título:**
```
6. Crear requirements.txt para el backend
```

**Cuerpo:**
```
## Descripción
El proyecto no tiene documentadas las dependencias de Python necesarias.

## Tareas
- [ ] Crear `requirements.txt` con todas las dependencias
- [ ] Incluir versiones específicas

## Dependencias necesarias
```
fastapi>=0.100.0
uvicorn>=0.23.0
pydantic>=2.0.0
pydantic-settings>=2.0.0
sqlmodel>=0.0.14
python-dotenv>=1.0.0
pytesseract>=0.3.10
pdf2image>=1.16.0
pillow>=10.0.0
easyocr>=1.7.0
requests>=2.28.0
```
```

---

## Issue 7: Agregar validación de importes extraídos

**Título:**
```
7. Agregar validación de importes extraídos
```

**Cuerpo:**
```
## Descripción
El parseo actual de importes puede ser inconsistente. Agregar validación para verificar que los importes extraídos sean correctos.

## Tareas
- [ ] Agregar función de validación que compare el total extraído con la suma de conceptos + IVA
- [ ] Retornar flag de validación en la respuesta
- [ ] Agregar logging de advertencias cuando hay discrepancias

## Endpoint a modificar
`POST /process-text/`

## Respuesta mejorada
```json
{
  "status": "success",
  "structured_data": {
    "concepto": "Luz",
    "deuda": 56.87,
    "tipo_factura": "Luz",
    "validacion": {
      "importe_ok": true,
      "total_calculado": 56.87,
      "total_declarado": 56.87
    }
  }
}
```
```

---

## Instrucciones para crear issues en GitHub

1. Ir a https://github.com/Elicupra/photo-finance/issues/new
2. Copiar el título de una issue
3. Copiar el cuerpo corresponding
4. Click en "Submit new issue"

**Nota:** Si el repositoriofork tiene issues deshabilitados, crear las issues en el repositorio original: https://github.com/Cortodem/photo-finance/issues/new