# zlibrary_to_notebooklm/book_parser.py

from .zlibrary import search_and_download_book
from .utils import parse_pdf_into_chunks


def book_to_notebook(title: str, author: str):
    """
    High-level helper:
    - search & download book
    - parse into chunks suitable for NotebookLM
    """

    # 1. Fetch PDF
    pdf_path = search_and_download_book(title, author)

    if not pdf_path:
        raise RuntimeError("fetch failed")

    # 2. Parse + chunk
    chunks = parse_pdf_into_chunks(pdf_path)

    if not chunks:
        raise RuntimeError("parse failed")

    return {
        "pdf_path": pdf_path,
        "chunks": chunks,
    }
