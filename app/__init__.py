from fastapi import FastAPI

app = FastAPI(title="Document RAG Backend")


@app.get("/")
def root():
    return {"message": "Document RAG Backend is running"}