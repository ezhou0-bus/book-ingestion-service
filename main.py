import os
import time
import traceback
from fastapi import FastAPI
from pydantic import BaseModel

# FastAPI app
app = FastAPI(title="Book Ingestion Service")

# Root endpoint for health checks
@app.get("/")
def root():
    return {"status": "Book ingestion service running"}

# Request model
class BookRequest(BaseModel):
    title: str
    author: str

# POST /upload_book endpoint
@app.post("/upload_book")
def upload_book(book: BookRequest):
    start_total = time.time()
    notebook_id = None

    print(f"\n=== Started ingestion for book: {book.title} by {book.author} ===")

    # Step 1: fetch PDF
    try:
        start = time.time()
        print("Step 1 - fetching PDF...")
        # TODO: Replace with actual PDF fetch logic
        time.sleep(1)  # simulate fetch
        print(f"Step 1 - fetch PDF done in {time.time() - start:.2f}s")
    except Exception as e:
        print("❌ Error in PDF fetch:", e)
        traceback.print_exc()
        return {
            "notebookId": None,
            "status": "error",
            "error_step": "fetch PDF",
            "error": str(e)
        }

    # Step 2: parse PDF
    try:
        start = time.time()
        print("Step 2 - parsing PDF...")
        # TODO: Replace with actual PDF parsing logic
        time.sleep(1)  # simulate parsing
        print(f"Step 2 - parse PDF done in {time.time() - start:.2f}s")
    except Exception as e:
        print("❌ Error in PDF parsing:", e)
        traceback.print_exc()
        return {
            "notebookId": None,
            "status": "error",
            "error_step": "parse PDF",
            "error": str(e)
        }

    # Step 3: chunk PDF
    try:
        start = time.time()
        print("Step 3 - chunking PDF for NotebookLM...")
        # TODO: Replace with actual chunking logic
        time.sleep(1)  # simulate chunking
        num_chunks = 5  # example
        print(f"Step 3 - chunking done in {time.time() - start:.2f}s, total chunks: {num_chunks}")
    except Exception as e:
        print("❌ Error in PDF chunking:", e)
        traceback.print_exc()
        return {
            "notebookId": None,
            "status": "error",
            "error_step": "chunking",
            "error": str(e)
        }

    # Step 4: generate NotebookLM summary
    try:
        start = time.time()
        print("Step 4 - sending chunks to NotebookLM for summary...")
        # TODO: Replace with actual NotebookLM integration
        time.sleep(1)  # simulate NotebookLM processing
        notebook_id = f"{book.title}-{book.author}".replace(" ", "_")
        print(f"Step 4 - NotebookLM summary done in {time.time() - start:.2f}s")
    except Exception as e:
        print("❌ Error in NotebookLM summary generation:", e)
        traceback.print_exc()
        return {
            "notebookId": None,
            "status": "error",
            "error_step": "NotebookLM summary",
            "error": str(e)
        }

    # Step 5: generate audio summary
    try:
        start = time.time()
        print("Step 5 - generating audio summary...")
        # TODO: Replace with actual audio generation
        time.sleep(1)  # simulate audio
        audio_file = f"{notebook_id}.mp3"
        print(f"Step 5 - audio summary done in {time.time() - start:.2f}s, file: {audio_file}")
    except Exception as e:
        print("❌ Error in audio generation:", e)
        traceback.print_exc()
        return {
            "notebookId": notebook_id,
            "status": "error",
            "error_step": "audio generation",
            "error": str(e)
        }

    # Total ingestion time
    total_time = time.time() - start_total
    print(f"=== Total ingestion time: {total_time:.2f}s ===\n")

    return {
        "notebookId": notebook_id,
        "status": "success",
        "total_time_s": round(total_time, 2)
    }


# Entry point for Render
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))  # Render dynamic port
    uvicorn.run("main:app", host="0.0.0.0", port=port, log_level="info")

