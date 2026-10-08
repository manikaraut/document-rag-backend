from fastapi import FastAPI

from app.api.chat import router as chat_router
from app.api.ingestion import router as ingestion_router


app = FastAPI(title="Document RAG Backend")

app.include_router(ingestion_router)
app.include_router(chat_router)


@app.get("/")
def root():
    return {"message": "Document RAG Backend is running"}