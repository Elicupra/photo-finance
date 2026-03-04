import datetime

from sqlmodel import SQLModel, Field, Session, create_engine
from sqlalchemy.orm import Session as AlchemySession
from .config import settings

# Configuración de la base de datos


class PDFFile(SQLModel, table=True):
    """Modelo para representar un archivo PDF en la base de datos"""
    id: int | None = Field(default=None, primary_key=True)
    filename: str
    filepath: str
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)
    contenido: str | None = None

class Factura(SQLModel, table=True):
    """Modelo para representar una factura extraída de un PDF"""
    id: int | None = Field(default=None, primary_key=True)
    pdf_file_id: int = Field(foreign_key="pdffile.id")
    numero_factura: str
    fecha_emision: datetime
    total: float
    ruc_emisor: str
    ruc_receptor: str

    #Relacion de factura con usuario
    usuario_id: int = Field(foreign_key="usuario.id")

    # Insertar nueva factura en la base de datos
    def insertar(self, session: AlchemySession):
        session.add(self)
        session.commit()
        session.refresh(self)

    # Modificar factura existente en la base de datos
    def modificar(self, session: AlchemySession, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        session.commit()
        session.refresh(self)

    # Eliminar factura de la base de datos
    def eliminar(self, session: AlchemySession):
        session.delete(self)
        session.commit()

    # Obtener factura por ID y por usuario
    @staticmethod
    def obtener_por_id(session: AlchemySession, factura_id: int, usuario_id: int):
        return session.query(Factura).filter(Factura.id == factura_id, Factura.usuario_id == usuario_id).first()
   
class Usuario(SQLModel, table=True):
    """Modelo para representar un usuario en la base de datos"""
    id: int | None = Field(default=None, primary_key=True)
    nombre: str
    email: str
    password_hash: str
    fecha_registro: datetime = Field(default_factory=datetime.utcnow)

# Crear el motor de la base de datos
engine = create_engine(settings.DATABASE_URL)

# Crear todas las tablas
SQLModel.metadata.create_all(engine)


