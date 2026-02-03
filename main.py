import traceback
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class BookRequest(BaseModel):
    title: str
    author: str

@app.post("/upload_book")
def upload_book(book: BookRequest):
    try:
        # Example: replace with actual book fetch
        notebook_id = f"{book.title}-{book.author}".replace(" ", "_")
        status = "success"
        return {"notebookId": notebook_id, "status": status}
    except Exception as e:
        # This will show detailed error in Render logs
        print("Error in /upload_book:", e)
        traceback.print_exc()
        return {"notebookId": None, "status": "error", "error": str(e)}
