from io import BytesIO
from typing import Literal

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from pypdf import PdfReader

from app.database.connection import SessionLocal
from app.database.models import Document
from app.services.chunking import chunk_text
from app.services.embedding import EmbeddingService
from app.services.vector_store import VectorStore


router = APIRouter(prefix="/documents", tags=["Documents"])

embedding_service = EmbeddingService()
vector_store = VectorStore()

vector_store.create_collection()


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    chunking_strategy: Literal["fixed", "sentence"] = Form("fixed"),
):
    """Upload, process, embed, store, and save document metadata."""

    if file.filename is None:
        raise HTTPException(
            status_code=400,
            detail="Filename is missing",
        )

    original_filename = file.filename
    filename = original_filename.lower()

    # -------------------------------------------------
    # 1. Validate file
    # -------------------------------------------------

    if not (filename.endswith(".pdf") or filename.endswith(".txt")):
        raise HTTPException(
            status_code=400,
            detail="Only PDF and TXT files are supported",
        )

    file_content = await file.read()

    # -------------------------------------------------
    # 2. Extract text
    # -------------------------------------------------

    if filename.endswith(".txt"):
        try:
            text = file_content.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise HTTPException(
                status_code=400,
                detail="TXT file must use UTF-8 encoding",
            ) from exc

        file_type = "txt"

    else:
        try:
            pdf_file = BytesIO(file_content)
            reader = PdfReader(pdf_file)

            text = ""

            for page in reader.pages:
                extracted_text = page.extract_text()

                if extracted_text:
                    text += extracted_text + "\n"

        except Exception as exc:
            raise HTTPException(
                status_code=400,
                detail="Could not read the PDF file",
            ) from exc

        file_type = "pdf"

    if not text.strip():
        raise HTTPException(
            status_code=400,
            detail="No text could be extracted from the document",
        )

    # -------------------------------------------------
    # 3. Create chunks
    # -------------------------------------------------

    chunks = chunk_text(
        text=text,
        strategy=chunking_strategy,
    )

    if not chunks:
        raise HTTPException(
            status_code=400,
            detail="No chunks were created from the document",
        )

    # -------------------------------------------------
    # 4. Generate embeddings
    # -------------------------------------------------

    embeddings = embedding_service.generate_embeddings(chunks)

    # -------------------------------------------------
    # 5. Store chunks + embeddings in Qdrant
    # -------------------------------------------------

    vector_store.add_documents(
        embeddings=embeddings,
        chunks=chunks,
        filename=original_filename,
    )

    # -------------------------------------------------
    # 6. Save document metadata in SQLite
    # -------------------------------------------------

    db = SessionLocal()

    try:
        document = Document(
            filename=original_filename,
            file_type=file_type,
            chunking_strategy=chunking_strategy,
            total_chunks=len(chunks),
            character_count=len(text),
        )

        db.add(document)
        db.commit()
        db.refresh(document)

        document_id = document.id

    except Exception as exc:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail="Failed to save document metadata",
        ) from exc

    finally:
        db.close()

    # -------------------------------------------------
    # 7. Return response
    # -------------------------------------------------

    return {
        "message": "Document processed successfully",
        "document_id": document_id,
        "filename": original_filename,
        "file_type": file_type,
        "chunking_strategy": chunking_strategy,
        "characters": len(text),
        "total_chunks": len(chunks),
        "embedding_dimensions": len(embeddings[0]),
    }