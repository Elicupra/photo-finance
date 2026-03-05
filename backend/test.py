import easyocr
from pdf2image import convert_from_path
import requests
import os
import dotenv


dotenv.load_dotenv()
# Use a path relative to this script for the sample PDF
HERE = os.path.dirname(__file__)
pdf_path = os.path.join(HERE, "container_pdf", "Naturgy_01_25.pdf")


def extract_pdf(pdf_path, lenguaje='es'):
    """Extrae texto con EasyOCR"""
    reader = easyocr.Reader([lenguaje])  # Spanish

    # Allow overriding/poppler location via the POPPLER_PATH env var
    poppler_path = os.getenv("POPPLER_PATH")
    if poppler_path:
        images = convert_from_path(pdf_path, poppler_path=poppler_path)
    else:
        images = convert_from_path(pdf_path)

    full_text = ""
    for page_num, image in enumerate(images):
        results = reader.readtext(image)
        text = "\n".join([text for (_, text, _) in results])
        full_text += f"\n--- Página {page_num + 1} ---\n{text}"

    print(full_text)


if __name__ == "__main__":
    extract_pdf(pdf_path)