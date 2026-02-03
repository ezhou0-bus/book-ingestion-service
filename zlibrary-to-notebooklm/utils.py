# zlibrary_to_notebooklm/utils.py
from pathlib import Path
import re

def count_words(text: str) -> int:
    chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
    english_words = len(re.findall(r'\b[a-zA-Z]+\b', text))
    return chinese_chars + english_words

def split_markdown_file(file_path: Path, max_words: int = 350000) -> list[Path]:
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    chapters = re.split(r'\n(?=#{1,3}\s)', content)

    chunks = []
    current_chunk = ""
    current_words = 0

    for chapter in chapters:
        chapter_words = count_words(chapter)
        if current_words + chapter_words > max_words:
            chunks.append(current_chunk)
            current_chunk = chapter
            current_words = chapter_words
        else:
            current_chunk += chapter
            current_words += chapter_words

    if current_chunk:
        chunks.append(current_chunk)

    chunk_files = []
    stem = file_path.stem
    for i, chunk in enumerate(chunks, 1):
        chunk_file = file_path.parent / f"{stem}_part{i}.md"
        with open(chunk_file, 'w', encoding='utf-8') as f:
            f.write(chunks[i-1])
        chunk_files.append(chunk_file)

    return chunk_files

