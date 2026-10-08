# Document RAG Backend

A modular FastAPI backend implementing document ingestion, vector search, conversational RAG, Redis memory, and interview booking.

## Features

- PDF/TXT document upload and text extraction
- Fixed-size and sentence-based chunking
- Text embeddings using Sentence Transformers
- Vector storage and similarity search with Qdrant
- Document metadata storage with SQLite + SQLAlchemy
- Custom RAG pipeline without `RetrievalQAChain`
- Multi-turn conversation memory using Redis
- Local LLM integration using Ollama
- Conversational interview booking with name, email, date, and time
- Automated tests

## Tech Stack

- **Backend:** FastAPI, Python
- **Embeddings:** Sentence Transformers (`all-MiniLM-L6-v2`)
- **Vector DB:** Qdrant
- **Memory:** Redis
- **LLM:** Ollama + Llama 3.2
- **Database:** SQLite + SQLAlchemy
- **PDF Processing:** pypdf

## Project Structure

```text
app/
├── api/
│   ├── chat.py
│   └── ingestion.py
├── database/
│   ├── connection.py
│   ├── init_db.py
│   └── models.py
├── services/
│   ├── booking.py
│   ├── chunking.py
│   ├── embedding.py
│   ├── llm.py
│   ├── rag.py
│   ├── redis_memory.py
│   └── vector_store.py
└── main.py

tests/
requirements.txt