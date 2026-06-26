from PyPDF2 import PdfReader
import os


def extract_text_from_resume(file_path: str):
    """
    Extract text from uploaded PDF resume.
    """

    if not os.path.exists(file_path):
        return ""

    text = ""

    try:
        reader = PdfReader(file_path)

        for page in reader.pages:
            extracted = page.extract_text()

            if extracted:
                text += extracted + "\n"

    except Exception as e:
        print("Resume parsing error:", e)

    return text.strip()