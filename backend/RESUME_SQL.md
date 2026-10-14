# RESUMEN - Persistencia de Datos en Base de Datos

## Estado Actual del Almacenamiento

### ✅ SQLite y Otros Motores (MariaDB/PostgreSQL) - PRECONFIGURADO

La configuración actual en `config.py` soporta dos modos de base de datos:

- **SQLite** (por defecto): `sqlite:///./pdf_database.db`
- **PostgreSQL**: Configurable vía variables de entorno `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_HOST`, `POSTGRES_PORT`, `POSTGRES_DB`

La URL de conexión se genera automáticamente mediante `Config.get_database_url()`, usando SQLAlchemy como capa de abstracción.

**Módulos involucrados:**
- `backend/config.py` - Configuración y generación de URLs
- `backend/models.py` - Modelos SQLAlchemy (`Documento`, `Pagina`, `DatabaseManager`)
- `backend/storage/database_storage.py` - Operaciones de guardado, búsqueda y eliminación
- `backend/main.py` - CLI que soporta `--storage database` o `--storage both`

**Dependencias** (requirements.txt):
- `sqlalchemy>=2.0.25`
- `psycopg2-binary==2.9.9` (para PostgreSQL)

### ❌ Pocketbase por API con Token - NO IMPLEMENTADO

**No hay integración actual** con Pocketbase en el código. No existen:
- Cliente de Pocketbase
- Manejo de tokens de autenticación
- Endpoints de API para collections/queries

**Qué se necesitaría añadir:**
- Cliente HTTP (httpx/aiohttp)
- Gestión de tokens de autenticación
- Endpoints para operaciones CRUD en collections de Pocketbase

## Estructura de Datos (Esquema Actual)

### Tabla `documentos`

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | Integer | Primary key, autoincrement |
| `nombre_archivo` | String(255) | Nombre del archivo PDF original |
| `ruta_archivo` | String(500) | Ruta absoluta del archivo PDF |
| `num_paginas` | Integer | Número total de páginas |
| `autor` | String(255) | Autor (opcional) |
| `titulo` | String(500) | Título (opcional) |
| `fecha_creacion` | DateTime | Fecha de creación (nullable) |
| `fecha_procesamiento` | DateTime | Fecha de procesamiento (default=utcnow) |

### Tabla `paginas`

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | Integer | Primary key, autoincrement |
| `documento_id` | Integer | ForeignKey → `documentos.id` |
| `numero_pagina` | Integer | Número de página (1-indexed) |
| `contenido` | Text | Texto extraído de la página |

### Relaciones

- **Uno-a-muchos**: Un `Documento` tiene muchas `Pagina` (`relationship("Pagina", back_populates="documento", cascade="all, delete-orphan")`)
- **Cascada de eliminación**: Al borrar un documento, sus páginas se eliminan automáticamente

## Operaciones de Persistencia

### Guardado (`DatabaseStorage.save_document()`)

1. Crea registro en tabla `documentos` con metadatos
2. Itera sobre `documento_data['paginas']` creando registros en tabla `paginas` asociados al documento
3. Retorna el `id` del documento guardado

### Recuperación (`DatabaseStorage.get_document()`)

- Por ID: `session.query(Documento).filter(Documento.id == doc_id).first()`
- Devuelve diccionario con todos los campos incluyendo páginas anidadas

### Listado (`DatabaseStorage.list_documents()`)

- Recupera todos los documentos con: id, nombre_archivo, num_paginas, título, autor, fecha_procesamiento

### Búsqueda (`DatabaseStorage.search_by_filename()`)

- Filtro SQL: `Documento.nombre_archivo.like(f'%{filename}%')`
- Útil para encontrar documentos por patrones de nombre

### Eliminación (`DatabaseStorage.delete_document()`)

- Elimina documento y sus páginas por cascade delete
- Retorna `True` siexistía y se eliminó, `False` si no existía

## Flujo de Procesamiento Completo

```mermaid
graph TD
    A[Subir PDF] --> B[extract_pdf() - PyPDF2]
    B --> C[parse_pdf_text - limpiar/extraer concepts]
    C --> D[text_to_json - generar JSON estructurado]
    D --> E{storage_type}
    E --> F[JSONStorage - ./output_json/*.json]
    E --> G[DatabaseStorage - SQLLite/.pdf_database.db o PostgreSQL]
    F & G --> H[Ambos formatos disponibles]
```

## ¿Qué persisten los datos?

**Sí.** Después de procesar una factura:

1. **JSON**: Se guardan archivos en `./output_json/` con nombre `{nombre_base}_{timestamp}.json`
2. **Base de datos**: Se guardan en tablas `documentos` + `paginas`:
   - Metadatos del documento (nombre, páginas, autor, título, fechas)
   - Contenido texto de cada página
3. **Ambas opciones son acumulativas** - nuevos PDFs añaden registros sin sobrescribir anteriores

## Comandos CLI disponibles

```bash
# Procesar y guardar solo en JSON
python main.py --storage json

# Procesar y guardar solo en base de datos
python main.py --storage database

# Procesar y guardar en ambos formatos
python main.py --storage both

# Listar documentos en JSON
python main.py --list json

# Listar documentos en base de datos
python main.py --list database
```

## Próximos pasos recomendados

1. **Pocketbase**: Si se necesita integración futura, añadir cliente HTTP y gestión de tokens
2. **Validación**: Ejecutar `python -m unittest test.unit_test.TestDatabaseStorage` para verificar operaciones BD
3. **PostgreSQL**: Probar con `DATABASE_TYPE=postgresql` y variables de entorno correspondientes