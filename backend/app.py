"""FastAPI app definition for PDF processing MVP."""

from pathlib import Path
import os
import tempfile

import dotenv
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

try:
    from backend.components import parse_pdf_text
    from backend.components.extract_pdf import extract_pdf
    from backend.components.text_to_json import text_to_json
except ModuleNotFoundError:
    # Fallback para ejecución desde la carpeta backend.
    from components import parse_pdf_text
    from components.extract_pdf import extract_pdf
    from components.text_to_json import text_to_json


dotenv.load_dotenv()

origins_env = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:4200")
CORS_ORIGINS = [origin.strip() for origin in origins_env.split(",") if origin.strip()]

app = FastAPI(title="PDF Reader Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class TextPayload(BaseModel):
    extracted_text: str


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}


@app.post("/process-pdf/")
async def process_pdf(file: UploadFile = File(...)) -> dict:
    """Recibe cualquier fichero; si es PDF, aplica OCR con Tesseract."""
    temp_file_path: Path | None = None

    try:
        contents = await file.read()
        suffix = Path(file.filename or "uploaded_file").suffix
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            temp_file.write(contents)
            temp_file_path = Path(temp_file.name)

        is_pdf = suffix.lower() == ".pdf" or file.content_type == "application/pdf"
        if not is_pdf:
            return {
                "status": "received",
                "filename": file.filename,
                "content_type": file.content_type,
                "message": "Archivo recibido. El OCR automático solo aplica a PDF.",
            }

        extracted_text = extract_pdf(str(temp_file_path), lenguaje="es", use_tesseract=True)
        return {
            "status": "success",
            "filename": file.filename,
            "content_type": file.content_type,
            "extracted_text": extracted_text,
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    finally:
        if temp_file_path and temp_file_path.exists():
            temp_file_path.unlink(missing_ok=True)


@app.post("/process-text/")
async def process_text(payload: TextPayload) -> dict:
    try:
        cleaned_text = parse_pdf_text.limpiar_texto(payload.extracted_text)
        concept = parse_pdf_text.find_concepts_keys(cleaned_text)
        debt = parse_pdf_text.parse_invoice_debt(cleaned_text)
        type_invoice = concept or "No especificado"
        json_data = text_to_json(concept, debt, type_invoice)
        return {"status": "success", "structured_data": json_data}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
