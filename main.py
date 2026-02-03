#!/usr/bin/env python3
"""
Main script to convert EPUB/PDF to Markdown and split for NotebookLM.
"""

import sys
from pathlib import Path
from zlibrary_to_notebooklm.convert_epub import epub_to_markdown
from zlibrary_to_notebooklm.utils import split_markdown_file, count_words

def process_book(book_file: Path):
    """Process EPUB/PDF book file"""
    if not book_file.exists():
        print(f"❌ File not found: {book_file}")
        return

    print(f"📖 Processing book: {book_file.name}")

    # Convert EPUB -> Markdown (PDFs are returned as-is)
    output_md = book_file.with_suffix(".md")
    epub_to_markdown(book_file, output_md)

    # Count words
    with open(output_md, 'r', encoding='utf-8') as f:
        text = f.read()
    total_words = count_words(text)
    print(f"ℹ️ Total words: {total_words:,}")

    # Split if too large
    if total_words > 350000:
        print("⚠️ File exceeds 350k words, splitting...")
        chunks = split_markdown_file(output_md)
    else:
        chunks = [output_md]

    print("\n✅ Processing complete! Output files:")
    for c in chunks:
        print(f" - {c}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py <path_to_book_file>")
        sys.exit(1)

    book_path = Path(sys.argv[1])
    process_book(book_path)

if __name__ == "__main__":
    main()

