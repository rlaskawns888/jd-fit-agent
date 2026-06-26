import io

import pdfplumber
from docx import Document

from app.core.exceptions import ApplicationError

def extract_text_from_file(filename: str, file_bytes: bytes) -> str:
    """
    업로드된 파일(pdf/docx/txt)에서 텍스트를 추출한다.
    파일 확장자를 기준으로 추출 방법을 분기한다.
    """
    lower_name = filename.lower()

    if lower_name.endswith(".pdf"):
        return _extract_from_pdf(file_bytes)
    elif lower_name.endswith(".docx"):
        return _extract_from_docx(file_bytes)
    elif lower_name.endswith(".txt"):
        return file_bytes.decode("utf-8", errors="ignore")
    else:
        raise ApplicationError(
            "지원하지 않는 파일 형식입니다. PDF, DOCX, TXT 파일만 업로드 가능합니다.",
            status_code=422,
        )


def _extract_from_pdf(file_bytes: bytes) -> str:
    """
    pdfplumber는 글자 좌표 기반으로 텍스트를 재구성해서,
    디자인이 들어간(아이콘, 특수 글머리 기호 등) PDF에서도
    pypdf보다 텍스트를 더 안정적으로 뽑아내는 경우가 많다.
    """
    pages_text = []

    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text() or ""
            pages_text.append(page_text)

    text = "\n".join(pages_text).strip()

    if not text:
        raise ApplicationError(
            "PDF에서 텍스트를 추출하지 못했습니다. "
            "스캔된 이미지 PDF는 지원하지 않습니다.",
            status_code=422,
        )

    return text


def _extract_from_docx(file_bytes: bytes) -> str:
    document = Document(io.BytesIO(file_bytes))
    paragraphs = [p.text for p in document.paragraphs if p.text.strip()]
    text = "\n".join(paragraphs).strip()

    if not text:
        raise ApplicationError(
            "DOCX에서 텍스트를 추출하지 못했습니다.",
            status_code=422,
        )

    return text
