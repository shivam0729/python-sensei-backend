# backend/app/parse_resume.py
from pdfminer.high_level import extract_text
import docx
import os

def parse_pdf(path: str):
    try:
        text = extract_text(path)
        return text
    except Exception:
        return ""

def parse_docx_file(path: str):
    try:
        document = docx.Document(path)
        text = "\n".join([para.text for para in document.paragraphs])
        return text
    except Exception:
        return ""

def parse_resume_file(path: str):
    ext = os.path.splitext(path)[1].lower()

    if ext == ".pdf":
        return parse_pdf(path)
    elif ext in [".doc", ".docx"]:
        return parse_docx_file(path)
    else:
        return ""
