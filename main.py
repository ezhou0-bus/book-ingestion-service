import os
import time
import traceback
from fastapi import FastAPI
from pydantic import BaseModel

# Supabase client
from supabase import create_client
import mimetypes

# Vendored zlibrary-to-notebooklm
from zlibrary_to_notebooklm.book_parser import book_to_notebook

# ----------------------------
# CONFIG
# ----------------------------
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
AUDIO_BUCKET = "books"  # Supabase storage bucket for audio

# ----------------------------
# HELPERS
# ----------------------------
def upload_audio_to_supabase(local_path, bucket=AUDIO_BUCKET, dest_path=None):
    """
    Uploads a local audio file to Supabase storage and returns the public URL.
    """
    if not dest_path:
        dest_path = os.path.basename(local_path)

    with open(local_path, "rb") as f:
        supabase_client.storage.from_(bucket).upload(dest_path, f, content_type=mimetypes.guess_type(local_path)[0])

    url = supabase_client.storage.from_(bucket).get_public_url(dest_path)
    return url

# ----------------------------
# FASTAPI APP
# ----------------------------
app = FastAPI(title="Book Ingestion Service")

# ----------------------------
# MODELS
# ----------------------------
class BookRequest(BaseModel):
    title: str
    author: str
    file_url: str = None  # optional, if uploading PDF/EPUB

# ----------------------------
# HEALTHCHECK
# ----------------------------
@app.get("/")
def root():
    return {"status": "Book ingestion service running"}

# ----------------------------
# UPLOAD BOOK ENDPOINT
# ----------------------------
@app.post("/upload_book")
def upload_book(book: BookRequest):
    start_total = time.time()
    notebook_id = None
    processing_steps = []

    print(f"\n=== Started ingestion for book: {book.title} by {book.author} ===")

    # Step 1: fetch book
    try:
        start = time.time()
        print("Step 1 - fetching book...")
        file_path = book.file_url  # optional external file URL
        # zlibrary handles download internally if file_path is None
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
            generate_audio=True
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

    # Step 3: save results to Supabase
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
        supabase_client.table("books").insert(book_record).execute()

        # Save chapters and upload audio
        for idx, chapter in enumerate(chapters):
            audio_url = None
            if audio_files and audio_files[idx]:
                audio_url = upload_audio_to_supabase(
                    audio_files[idx],
                    bucket=AUDIO_BUCKET,
                    dest_path=f"{notebook_id}_chapter{idx}.mp3"
                )

            supabase_client.table("chapters").insert({
                "book_id": notebook_id,
                "chapter_idx": idx,
                "title": chapter.get("title"),
                "summary": chapter.get("summary"),
                "audio_url": audio_url
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
# ENTRY POINT FOR RENDER
# ----------------------------
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))  # dynamic Render port
    uvicorn.run("main:app", host="0.0.0.0", port=port, log_level="info")
