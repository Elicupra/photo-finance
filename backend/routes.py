""""Routes para el backend de lectura de PDFs"""
import os

from fastapi import APIRouter, UploadFile, File, HTTPException
from sqlalchemy.orm import Session

from .models import PDFFile, Factura, Usuario
from .database import get_db

# Crear el router para las rutas del backend
router = APIRouter()

# Ruta para subir un archivo PDF
@router.post("/upload-pdf/")
async def upload_pdf(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Ruta para subir un archivo PDF y guardarlo en la base de datos"""
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="El archivo debe ser un PDF")
    
    # Guardar el archivo PDF en el sistema de archivos
    file_location = f"{settings.FILE_PDF_PATH}/{file.filename}"
    with open(file_location, "wb") as f:
        f.write(await file.read())
    
    # Crear una nueva entrada en la base de datos para el archivo PDF
    pdf_file = PDFFile(filename=file.filename, filepath=file_location)
    db.add(pdf_file)
    db.commit()
    db.refresh(pdf_file)

    return {"message": "Archivo PDF subido exitosamente", "pdf_file_id": pdf_file.id}

# Ruta para obtener todos los archivos PDF
@router.get("/pdf-files/")
def get_pdf_files(db: Session = Depends(get_db)):
    """Ruta para obtener todos los archivos PDF guardados"""
    pdf_files = db.query(PDFFile).all()
    return pdf_files

# Ruta para obtener un archivo PDF específico por ID
@router.get("/pdf-files/{pdf_file_id}")
def get_pdf_file(pdf_file_id: int, db: Session = Depends(get_db)):
    """Ruta para obtener un archivo PDF específico por ID"""
    pdf_file = db.query(PDFFile).filter(PDFFile.id == pdf_file_id).first()
    if not pdf_file:
        raise HTTPException(status_code=404, detail="Archivo PDF no encontrado")
    return pdf_file

# Ruta para eliminar un archivo PDF por ID
@router.delete("/pdf-files/{pdf_file_id}")
def delete_pdf_file(pdf_file_id: int, db: Session = Depends(get_db)):
    """Ruta para eliminar un archivo PDF por ID"""
    pdf_file = db.query(PDFFile).filter(PDFFile.id == pdf_file_id).first()
    if not pdf_file:
        raise HTTPException(status_code=404, detail="Archivo PDF no encontrado")
    
    # Eliminar el archivo PDF del sistema de archivos
    os.remove(pdf_file.filepath)
    
    # Eliminar la entrada del archivo PDF de la base de datos
    db.delete(pdf_file)
    db.commit()
    
    return {"message": "Archivo PDF eliminado exitosamente"}

# Ruta para obtener todas las facturas de un usuario específico
@router.get("/facturas/")
def get_facturas(usuario_id: int, db: Session = Depends(get_db)):
    """Ruta para obtener todas las facturas de un usuario específico"""
    facturas = db.query(Factura).filter(Factura.usuario_id == usuario_id).all()
    return facturas

# Ruta para obtener una factura específica por ID y usuario
@router.get("/facturas/{factura_id}")
def get_factura(factura_id: int, usuario_id: int, db: Session = Depends(get_db)):
    """Ruta para obtener una factura específica por ID y usuario"""
    factura = db.query(Factura).filter(Factura.id == factura_id, Factura.usuario_id == usuario_id).first()
    if not factura:
        raise HTTPException(status_code=404, detail="Factura no encontrada")
    return factura

# Ruta para eliminar una factura por ID y usuario
@router.delete("/facturas/{factura_id}")
def delete_factura(factura_id: int, usuario_id: int, db: Session = Depends(get_db)):
    """Ruta para eliminar una factura por ID y usuario"""
    factura = db.query(Factura).filter(Factura.id == factura_id, Factura.usuario_id == usuario_id).first()
    if not factura:
        raise HTTPException(status_code=404, detail="Factura no encontrada")
    
    # Eliminar la factura de la base de datos
    db.delete(factura)
    db.commit()
    
    return {"message": "Factura eliminada exitosamente"}