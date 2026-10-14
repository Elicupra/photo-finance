# Issues - Backend MVP Facturas

## Estado del Test

### Test de Backend: ✅ FUNCIONAL
- `GET /health` - OK
- `POST /process-pdf/` - OK (extrae texto OCR)
- `POST /process-text/` - OK (parsea a JSON)

**Salida actual:**
```json
{
  "concepto": "Luz",
  "deuda": 56.87,
  "tipo_factura": "Luz"
}
```

---

## Issues Encontrados

### 1. CRÍTICO: Frontend sin integración con backend
**Severidad:** Alta
**Descripción:** El componente `UploadInvoiceComponent` no tiene llamadas HTTP al backend. Solo previsualiza el archivo localmente.

**Ubicación:** `src/app/component/upload-invoice.component/upload-invoice.component.ts:41-46`
```typescript
save() {
  console.log("Archivo subido: ", this.invoicePreview);
  console.log("objeto", this.invoiceFile);
  // FALTA: Llamada HTTP al backend
}
```

### 2. CRÍTICO: routes.py tiene errores de importación
**Severidad:** Alta
**Descripción:** Las rutas usan `Depends(get_db)` y `settings` sin importarlos correctamente.

**Ubicación:** `routes.py:5,21`
```python
# Error: falta importar Depends
from fastapi import APIRouter, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from .models import PDFFile, Factura, Usuario
from .database import get_db  # FALTA: Este módulo no existe

# Error: settings usado pero no existe
file_location = f"{settings.FILE_PDF_PATH}/{file.filename}"
```

### 3. MEDIO: config.py vacío
**Severidad:** Media
**Descripción:** `config.py` está vacío pero `models.py` intenta importar `settings` de él.

**Ubicación:** `models.py:5`, `config.py`

### 4. BAJO: Dependencias no documentadas
**Severidad:** Baja
**Descripción:** No existe `requirements.txt` ni `pyproject.toml` para gestionar dependencias.

---

## Plan para Corregir Integración Frontend-Backend

### Paso 1: Crear servicio HTTP en Angular
```typescript
// src/app/services/invoice.service.ts
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({ providedIn: 'root' })
export class InvoiceService {
  private apiUrl = 'http://localhost:8000';

  constructor(private http: HttpClient) {}

  processPdf(file: File): Observable<any> {
    const formData = new FormData();
    formData.append('file', file);
    return this.http.post(`${this.apiUrl}/process-pdf/`, formData);
  }

  processText(text: string): Observable<any> {
    return this.http.post(`${this.apiUrl}/process-text/`, { extracted_text: text });
  }
}
```

### Paso 2: Actualizar UploadInvoiceComponent
```typescript
import { InvoiceService } from '../services/invoice.service';

constructor(private invoiceService: InvoiceService) {}

save() {
  if (this.invoiceFile) {
    this.invoiceService.processPdf(this.invoiceFile).subscribe({
      next: (response) => {
        console.log('PDF procesado:', response);
        // Navegar a pantalla de resumen
      },
      error: (err) => console.error('Error:', err)
    });
  }
}
```

### Paso 3: Habilitar HttpClient en Angular
En `app.config.ts`:
```typescript
import { provideHttpClient } from '@angular/common/http';

export const appConfig: ApplicationConfig = {
  providers: [provideHttpClient()]
};
```

### Paso 4: Configurar CORS en backend
El backend ya tiene CORS configurado para `localhost:3000` y `localhost:4200` en `app.py:25-26`.

---

## Recomendaciones

1. **No usar `routes.py`** - Crear nuevo módulo de rutas correctamente o integrar en `app.py`
2. **Completar `config.py`** - Definir settings de configuración
3. **Crear `requirements.txt`** - Documentar dependencias
4. **Agregar validación** - Verificar que la deuda extraída coincida con el total de la factura