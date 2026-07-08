from pathlib import Path
import fitz


def extract_pdf_pages(file_bytes: bytes) -> list[dict]:
    """Return list of {page, text} extracted from PDF bytes."""
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    pages: list[dict] = []
    for idx, page in enumerate(doc, start=1):
        text = page.get_text("text").strip()
        if text:
            pages.append({"page": idx, "text": text})
    return pages


def save_upload(upload_dir: str, document_id: str, filename: str, file_bytes: bytes) -> str:
    Path(upload_dir).mkdir(parents=True, exist_ok=True)
    safe_name = filename.replace("/", "_").replace("\\", "_")
    path = Path(upload_dir) / f"{document_id}_{safe_name}"
    path.write_bytes(file_bytes)
    return str(path)
