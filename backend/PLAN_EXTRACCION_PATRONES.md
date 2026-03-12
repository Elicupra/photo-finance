# Plan Iterado de Extraccion de Patrones

## Objetivo

Clasificar de forma simple el texto OCR extraido de un PDF para obtener un resultado util como:

```text
Suministro: Luz
Total a Pagar: 65
Fecha Vencimiento: 31/03/2026
```

La idea es mantener una solucion sencilla, controlada y facil de depurar.

## Foco Actual

- No usar logica compleja.
- No usar NLP.
- No intentar extraer todo a la vez.
- Empezar por patrones cerrados y faciles de validar.
- Reutilizar las funciones actuales del modulo siempre que sea posible.

## Estado Actual

Ya existe una base funcional para:

- extraer texto OCR del PDF
- obtener el total a pagar
- obtener la fecha de vencimiento
- buscar conceptos con `find_concepts_keys`

El siguiente avance natural es mejorar la clasificacion del concepto sin perder simplicidad.

## Iteracion 1

### Objetivo

Detectar patrones directos dentro del texto OCR.

### Alcance

- Buscar palabras como `luz` o `electricidad`
- Devolver una salida simple y clara

### Ejemplo esperado

```text
Suministro: Luz
```

### Regla simple

Si en el texto aparece `luz` o `electricidad`, el resultado debe normalizarse a:

```text
Suministro: Luz
```

### Ventaja

- Facil de probar
- Facil de corregir
- Facil de ampliar

## Iteracion 2

### Objetivo

Pasar de una lista plana de patrones a una clasificacion por categorias y subcategorias.

### Estructura conceptual

```text
Suministros:
    Luz
    Gas
    Agua

Telecomunicaciones:
    Fibra
    Telefono

Alimentacion:
    Supermercado
    Productos
```

### Ejemplos de mapeo

- `luz`, `electricidad` -> `Suministros > Luz`
- `fibra`, `internet` -> `Telecomunicaciones > Fibra`
- `telefono`, `movil` -> `Telecomunicaciones > Telefono`
- `supermercado`, `hipermercado` -> `Alimentacion > Supermercado`

### Objetivo tecnico

Que la funcion siga siendo sencilla, pero que ya no dependa de una sola lista desordenada.

## Iteracion 3

### Objetivo

Guardar los patrones en SQLite para que el modulo Python los lea desde una base de datos en lugar de escribirlos todos a mano dentro del codigo.

### Enfoque recomendado

Usar SQLite como catalogo de patrones, no como motor complejo de analisis.

### Idea base

Una tabla sencilla puede almacenar:

- categoria
- subcategoria
- patron
- valor_salida
- prioridad

### Ejemplo conceptual

```text
categoria: Suministros
subcategoria: Luz
patron: luz
valor_salida: Suministro: Luz

categoria: Suministros
subcategoria: Luz
patron: electricidad
valor_salida: Suministro: Luz
```

### Flujo

1. El OCR extrae el texto.
2. Python normaliza el texto.
3. Python carga patrones desde SQLite.
4. Python compara texto contra esos patrones.
5. Python construye la salida final.

## Iteracion 4

### Objetivo

Agregar sublistas de productos dentro de algunas categorias concretas.

### Ejemplo

```text
Alimentacion:
    Supermercado
    Productos:
        Pan
        Leche
        Huevos
```

### Aclaracion importante

Esto solo debe hacerse con listas cerradas de productos. Si se intenta detectar cualquier producto libre del OCR, la complejidad sube mucho y se pierde el enfoque actual.

## Propuesta de Arquitectura Simple

### Parte 1: Extraccion

- `extract_pdf()` obtiene el texto OCR

### Parte 2: Datos concretos

- `parse_invoice_debt()` obtiene el total
- `parse_invoice_debt_date()` obtiene la fecha

### Parte 3: Clasificacion

- `find_concepts_keys()` detecta el concepto principal
- mas adelante puede apoyarse en una tabla SQLite

### Parte 4: Salida final

Construir un resultado compacto como:

```text
Suministro: Luz
Total a Pagar: 65
Fecha Vencimiento: 31/03/2026
```

## Decision Recomendada Ahora

El siguiente paso mas razonable es este:

1. Consolidar bien la deteccion simple de `luz` y `electricidad`.
2. Definir una estructura de categorias y subcategorias.
3. Mover esa estructura a SQLite solo cuando el mapeo base ya este claro.

## Lo Que No Conviene Hacer Aun

- consultas SQLite complejas por cada linea del OCR
- expresiones regulares demasiado largas
- clasificacion abierta con demasiadas categorias desde el principio
- extraccion libre de productos no controlados

## Siguiente Paso Sugerido

Cuando quieras continuar, el siguiente entregable util seria definir una tabla SQLite minima y una funcion Python corta que lea esos patrones y devuelva la categoria principal detectada.

## TODO - Siguiente Mejora (Productos No Catalogados)

### Objetivo

Si durante la lectura OCR aparece un producto o termino relevante que no exista en los patrones guardados en SQLite, debe detectarse como no catalogado.

### Comportamiento Esperado

1. Comparar texto OCR contra los patrones actuales de SQLite.
2. Si hay terminos candidatos no reconocidos, marcarlos como pendientes de revision.
3. Emitir notificacion en consola para dos perfiles:
    - Admin: detalle tecnico del termino detectado y contexto.
    - Usuario: mensaje simple indicando que se encontro un concepto no clasificado.

### Salida Minima en Consola (simplificada)

```text
[ADMIN] Nuevo termino no catalogado detectado: "xxxx"
[ADMIN] Contexto OCR: "...fragmento de texto..."
[USUARIO] Hemos detectado un concepto no clasificado. Se revisara para mejorar la clasificacion.
```

### TODO Interno

Evaluar la posibilidad de alta en SQLite desde el modulo Python, pero siempre bajo flujo revisado.

### Reglas de Seguridad para Alta en SQLite

- No insertar automaticamente en produccion.
- Guardar propuesta de alta como pendiente.
- Requerir revision previa antes de confirmar insercion.
- Registrar fecha, termino y origen del OCR para auditoria.

### Propuesta de Implementacion Gradual

1. Fase 1: deteccion y log en consola.
2. Fase 2: guardar propuestas pendientes en una tabla de revision.
3. Fase 3: herramienta de aprobacion para insertar en tabla de patrones.