from PyPDF2 import PdfReader
from pathlib import Path

def read_pdf_text(file_path: str) -> str:
    p = Path(file_path)
    if not p.exists():
        raise FileNotFoundError(f"PDF not found: {file_path}")
    try:
        reader = PdfReader(str(p))
        return "\n".join((page.extract_text() or "") for page in reader.pages).strip()
    except Exception as e:
        raise RuntimeError(f"PDF read error: {e}")
