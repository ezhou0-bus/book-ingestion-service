from .zlibrary import search_and_download_book
from .utils import parse_pdf_into_chunks


def book_to_notebook(title: str, author: str):
    pdf_path = search_and_download_book(title, author)
    if not pdf_path:
        raise RuntimeError("fetch failed")

    chunks = parse_pdf_into_chunks(pdf_path)
    if not chunks:
        raise RuntimeError("parse failed")

    return {
        "pdf_path": pdf_path,
        "chunks": chunks,
    }
