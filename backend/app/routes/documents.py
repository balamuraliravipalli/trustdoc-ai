import os
import uuid
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session
from app.core.config import get_settings
from app.core.security import require_api_key, require_admin
from app.db.models import Document, Chunk
from app.db.session import get_db
from app.schemas import DocumentOut, ChunkOut
from app.services.chunker import chunk_pages, estimate_tokens
from app.services.openai_client import OpenAIService
from app.services.pdf import extract_pdf_pages, save_upload
from app.services.vector_store import VectorStore

router = APIRouter(prefix="/api/documents", tags=["documents"], dependencies=[Depends(require_api_key)])


@router.get("", response_model=list[DocumentOut])
def list_documents(db: Session = Depends(get_db)):
    docs = db.query(Document).order_by(Document.created_at.desc()).all()
    return [
        DocumentOut(
            id=d.id,
            filename=d.filename,
            document_type=d.document_type,
            page_count=d.page_count,
            chunk_count=d.chunk_count,
            created_at=d.created_at.isoformat(),
        )
        for d in docs
    ]


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    document_type: str = Form(default="general"),
    db: Session = Depends(get_db),
    _admin = Depends(require_admin),
):
    document_type = (document_type or "general").strip() or "general"
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    settings = get_settings()
    file_bytes = await file.read()
    document_id = str(uuid.uuid4())
    storage_path = save_upload(settings.upload_dir, document_id, file.filename, file_bytes)

    pages = extract_pdf_pages(file_bytes)
    if not pages:
        raise HTTPException(status_code=400, detail="Could not extract text from this PDF")

    chunks = chunk_pages(pages, settings.max_chunk_words, settings.chunk_overlap_words)
    if not chunks:
        raise HTTPException(status_code=400, detail="No text chunks were created from this PDF")

    doc = Document(
        id=document_id,
        filename=file.filename,
        document_type=document_type,
        page_count=len(pages),
        chunk_count=len(chunks),
        storage_path=storage_path,
    )
    db.add(doc)

    db_chunks: list[Chunk] = []
    for ch in chunks:
        db_chunk = Chunk(
            id=str(uuid.uuid4()),
            document_id=document_id,
            filename=file.filename,
            document_type=document_type,
            page=ch.page,
            chunk_index=ch.chunk_index,
            text=ch.text,
            token_estimate=estimate_tokens(ch.text),
        )
        db.add(db_chunk)
        db_chunks.append(db_chunk)

    db.commit()

    openai = OpenAIService()
    vector_store = VectorStore()
    embeddings = openai.embed_texts([c.text for c in db_chunks])
    points = []
    for db_chunk, embedding in zip(db_chunks, embeddings):
        points.append({
            "id": db_chunk.id,
            "vector": embedding,
            "payload": {
                "chunk_id": db_chunk.id,
                "document_id": document_id,
                "filename": file.filename,
                "document_type": document_type,
                "document_type_normalized": document_type.lower(),
                "page": db_chunk.page,
                "chunk_index": db_chunk.chunk_index,
            },
        })
    vector_store.upsert_chunks(points)

    return {
        "document_id": document_id,
        "filename": file.filename,
        "document_type": document_type,
        "pages": len(pages),
        "chunks": len(chunks),
        "message": "Document uploaded and indexed successfully",
    }


@router.get("/{document_id}/chunks", response_model=list[ChunkOut])
def list_document_chunks(document_id: str, db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    chunks = db.query(Chunk).filter(Chunk.document_id == document_id).order_by(Chunk.page, Chunk.chunk_index).all()
    return [
        ChunkOut(
            id=c.id,
            page=c.page,
            chunk_index=c.chunk_index,
            token_estimate=c.token_estimate,
            text_preview=(c.text[:500] + "...") if len(c.text) > 500 else c.text,
        )
        for c in chunks
    ]


@router.delete("/{document_id}")
def delete_document(document_id: str, db: Session = Depends(get_db), _admin = Depends(require_admin)):
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    VectorStore().delete_document(document_id)
    try:
        if doc.storage_path and os.path.exists(doc.storage_path):
            os.remove(doc.storage_path)
    except OSError:
        pass
    db.delete(doc)
    db.commit()
    return {"message": "Document deleted", "document_id": document_id}
