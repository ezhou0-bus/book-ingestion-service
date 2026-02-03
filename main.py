import os
import traceback
from fastapi import FastAPI
from pydantic import BaseModel

# Create FastAPI app
app = FastAPI(title="Book Ingestion Service")

# Root endpoint for Render health checks
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
    try:
        # Placeholder logic
        notebook_id = f"{book.title}-{book.author}".replace(" ", "_")
        status = "success"

        # Return JSON response
        return {"notebookId": notebook_id, "status": status}

    except Exception as e:
        # Log full traceback to Render logs
        print("Error in /upload_book:", e)
        traceback.print_exc()
        return {"notebookId": None, "status": "error", "error": str(e)}

# Entry point
if __name__ == "__main__":
    import uvicorn
    # Use PORT provided by Render, fallback to 8000 locally
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, log_level="info")
