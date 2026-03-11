import sys
sys.path.append('.')
from test import extract_pdf
import os

pdf_path = os.path.join('container_pdf', 'Naturgy_01_25.pdf')
print("Extrayendo texto...")
texto = extract_pdf(pdf_path)

# Mostrar líneas numeradas para análisis
lineas = texto.split('\n')
print(f"\nTotal de líneas: {len(lineas)}\n")

# Buscar líneas relevantes
print("=" * 80)
print("LÍNEAS CON INFORMACIÓN IMPORTANTE:")
print("=" * 80)

keywords = ['factura', 'fecha', 'total', 'periodo', 'referencia', 'punta', 'llano', 'valle', 
            'pagar', 'electricidad', 'iva', 'dirección', 'suministro', 'consumo']

for i, line in enumerate(lineas):
    line_lower = line.lower()
    if any(kw in line_lower for kw in keywords):
        print(f"Línea {i:3d}: {line[:100]}")

print("\n" + "=" * 80)
print("PRIMEROS 100 LÍNEAS PARA CONTEXTO:")
print("=" * 80)
for i in range(min(100, len(lineas))):
    print(f"{i:3d}: {lineas[i][:80]}")
