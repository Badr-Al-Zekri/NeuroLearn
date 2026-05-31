from io import BytesIO
from pypdf import PdfReader


class PdfExtractionError(ValueError):
    pass


def extract_pdf_text(data: bytes) -> str:
    try:
        reader = PdfReader(BytesIO(data))
    except Exception as exc:
        raise PdfExtractionError("The uploaded PDF could not be read.") from exc

    pages: list[str] = []
    for page in reader.pages:
        text = page.extract_text() or ""
        if text.strip():
            pages.append(text.strip())

    content = "\n\n".join(pages).strip()
    if len(content.split()) < 20:
        raise PdfExtractionError("No readable text was found. Scanned PDFs are not supported in this demo.")
    return content

