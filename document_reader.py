"""Text extraction helpers for PDFs and plain text."""
from pathlib import Path

def read_document(path: str) -> str:
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(file_path)

    suffix = file_path.suffix.lower()
    if suffix == ".txt":
        return file_path.read_text(encoding="utf-8")

    if suffix == ".pdf":
        try:
            import fitz
        except ImportError as exc:
            raise RuntimeError("Install PyMuPDF with: pip install PyMuPDF") from exc

        chunks = []
        with fitz.open(file_path) as doc:
            for page_number, page in enumerate(doc, start=1):
                page_text = page.get_text("text")
                chunks.append(f"--- Page {page_number} ---\\n{page_text}")
        text = "\\n".join(chunks).strip()
        if not text:
            raise ValueError(
                "No selectable text found in this PDF. It may be scanned; OCR is not included in this prototype."
            )
        return text

    raise ValueError("Supported document formats are .txt and text-based .pdf")
