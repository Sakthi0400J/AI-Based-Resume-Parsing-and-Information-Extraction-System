import os
import pdfplumber
from docx import Document

def extract_text_from_file(file_path):
   
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".pdf":
        return _extract_pdf(file_path)

    elif ext == ".docx":
        return _extract_docx(file_path)

    elif ext == ".txt":
        return _extract_txt(file_path)

    else:
        raise ValueError(f"Unsupported file format: '{ext}'. Supported formats: PDF, DOCX, TXT.")


def _extract_pdf(file_path):
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    if not text.strip():
        raise ValueError("PDF appears to be empty or scanned (no extractable text).")
    return text


def _extract_docx(file_path):
    doc = Document(file_path)
    paragraphs = [para.text for para in doc.paragraphs if para.text.strip()]
    if not paragraphs:
        raise ValueError("DOCX file appears to be empty.")
    return "\n".join(paragraphs)


def _extract_txt(file_path):
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        text = f.read()
    if not text.strip():
        raise ValueError("TXT file appears to be empty.")
    return text
