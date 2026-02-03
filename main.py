import os
import time
import traceback
from fastapi import FastAPI
from pydantic import BaseModel

import supabase
from supabase import create_client
from zlibrary_to_notebooklm import book_to_notebook  # core ingestion function

# ----------------------------
# CONFIG
# ----------------------------
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)

# FastAPI app
app = FastAPI(title="Book Ingestion Service")

# ----------------------------
# MODELS
# ----------------------------
class BookRequest(BaseModel):
    title: str
    author: str
    file_url: str = None  # Optional, if uploading PDF/EPUB

# ----------------------------
# HEALTHCHECK
# ----------------------------
@app.get("/")
def root():
    return {"status": "Book ingestion service running"}

# ----------------------------
# UPLOAD BOOK
# ----------------------------
@app.post("/upload_book")
def upload_book(book: BookRequest):
    start_total = time.time()
    notebook_id = None

    print(f"\n=== Started ingestion for book: {book.title} by {book.author} ===")
    processing_steps = []

    # Step 1: fetch book
    try:
        start = time.time()
        print("Step 1 - fetching book...")
        # zlibrary handles download internally if file_url not provided
        file_path = book.file_url  # If provided, else zlibrary fetches by title/author
        processing_steps.append({"id": "fetch_book", "label": "Fetch book (Render.com)", "status": "done"})
        print(f"Step 1 - done in {time.time() - start:.2f}s")
    except Exception as e:
        print("❌ Error fetching book:", e)
        traceback.print_exc()
        processing_steps.append({"id": "fetch_book", "label": "Fetch book", "status": "error"})
        return {
            "notebookId": None,
            "status": "error",
            "error_step": "fetch_book",
            "error": str(e),
            "processing_steps": processing_steps
        }

    # Step 2: generate NotebookLM summary + audio
    try:
        start = time.time()
        print("Step 2 - generating NotebookLM summary & audio...")
        notebook_id, chapters, audio_files = book_to_notebook(
            title=book.title,
            author=book.author,
            file_path=file_path,
            generate_audio=True  # generate mp3 files
        )
        processing_steps.append({"id": "generate", "label": "Generate summary & audio", "status": "done"})
        print(f"Step 2 - done in {time.time() - start:.2f}s")
    except Exception as e:
        print("❌ Error generating summary/audio:", e)
        traceback.print_exc()
        processing_steps.append({"id": "generate", "label": "Generate summary & audio", "status": "error"})
        return {
            "notebookId": notebook_id,
            "status": "error",
            "error_step": "generate",
            "error": str(e),
            "processing_steps": processing_steps
        }

    # Step 3: save results to Superbase
    try:
        start = time.time()
        print("Step 3 - saving results to Supabase...")
        # Save book record
        book_record = {
            "title": book.title,
            "author": book.author,
            "status": "success",
            "notebook_id": notebook_id,
            "file_url": book.file_url,
            "processing_steps": str(processing_steps)
        }
        res = supabase_client.table("books").insert(book_record).execute()

        # Save chapters
        for idx, chapter in enumerate(chapters):
            supabase_client.table("chapters").insert({
                "book_id": notebook_id,
                "chapter_idx": idx,
                "title": chapter.get("title"),
                "summary": chapter.get("summary"),
                "audio_url": audio_files[idx] if audio_files else None
            }).execute()

        processing_steps.append({"id": "save", "label": "Save results", "status": "done"})
        print(f"Step 3 - done in {time.time() - start:.2f}s")
    except Exception as e:
        print("❌ Error saving to Supabase:", e)
        traceback.print_exc()
        processing_steps.append({"id": "save", "label": "Save results", "status": "error"})
        return {
            "notebookId": notebook_id,
            "status": "error",
            "error_step": "save",
            "error": str(e),
            "processing_steps": processing_steps
        }

    total_time = time.time() - start_total
    print(f"=== Total ingestion time: {total_time:.2f}s ===\n")

    return {
        "notebookId": notebook_id,
        "status": "success",
        "processing_steps": processing_steps,
        "total_time_s": round(total_time, 2)
    }

# ----------------------------
# ENTRY POINT
# ----------------------------
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))  # Render dynamic port
    uvicorn.run("main:app", host="0.0.0.0", port=port, log_level="info")
