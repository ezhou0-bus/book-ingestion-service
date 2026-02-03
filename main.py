from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

# Request body model
class BookRequest(BaseModel):
    title: str
    author: str

@app.post("/upload_book")
def upload_book(book: BookRequest):
    # Placeholder: in real app, you would call your NotebookLM bridge
    notebook_id = f"{book.title}-{book.author}".replace(" ", "_")
    status = "success"

    return {"notebookId": notebook_id, "status": status}
