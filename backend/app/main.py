from fastapi import Depends, FastAPI, HTTPException, UploadFile, File
from pypdf import PdfReader
from sqlalchemy.orm import Session
from .database import get_db
from .models import Document, DocumentChunk
from .schemas import DocumentCreate, DocumentUpdate, DocumentResponse, ChatRequest, ChatResponse
from .chunking import chunk_text, retrieve_chunks
from .rag import generate_rag_response, build_sources
from .embeddings import create_embeddings, create_embedding
from .config import settings
from .pinecone_client import index, delete_document_vectors
import logging
from fastapi.middleware.cors import CORSMiddleware
from .router import route_question
from .ollama_client import generate_response

logger = logging.getLogger(__name__)



app = FastAPI(title="AI Knowledge Agent")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
) 

@app.get("/")
def root():
    return {"message": "AI Knowledge Agent API"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/documents")
def create_document(
    document: DocumentCreate,
    db: Session = Depends(get_db),
):
    new_document = Document(
        filename=document.filename,
        content=document.content,
    )

    db.add(new_document)
    db.commit()
    db.refresh(new_document)

    return new_document

@app.get("/documents")
def get_documents(db: Session = Depends(get_db)):
    return db.query(Document).all()


@app.get("/chunks")
def get_chunks(db: Session = Depends(get_db)):
    return db.query(DocumentChunk).all()



@app.get(
    "/documents/{document_id}",
    response_model=DocumentResponse,
)
def get_document(
    document_id: int,
    db: Session = Depends(get_db),
):
    document = db.query(Document).filter(
        Document.id == document_id
    ).first()

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found",
        )

    return document



@app.delete("/documents/{document_id}")
def delete_document(
    document_id: int,
    db: Session = Depends(get_db),
):
    document = db.query(Document).filter(
        Document.id == document_id
    ).first()

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found",
        )

    try:
        delete_document_vectors(document_id)

        db.delete(document)
        db.commit()

        return {"message": "Document deleted"}

    except Exception:
        db.rollback()

        logger.exception(
            "Failed to delete document %s",
            document_id,
        )

        raise HTTPException(
            status_code=500,
            detail="Failed to delete document",
        )


@app.put("/documents/{document_id}")
def update_document(
    document_id: int,
    document_data: DocumentUpdate,
    db: Session = Depends(get_db),
):
    document = db.query(Document).filter(
        Document.id == document_id
    ).first()

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found",
        )

    try:
        # 1. Delete old vectors from Pinecone
        delete_document_vectors(document_id)

        # 2. Update document
        document.filename = document_data.filename
        document.content = document_data.content

        # 3. Delete old chunks
        document.chunks.clear()

        # 4. Create new chunks
        chunks = chunk_text(document_data.content)

        if not chunks:
            raise HTTPException(
                status_code=400,
                detail="The document could not be split into chunks",
            )

        # 5. Create embeddings
        embeddings = create_embeddings(chunks)

        # 6. Save new chunks
        db_chunks = []

        for i, chunk in enumerate(chunks):
            new_chunk = DocumentChunk(
                document_id=document_id,
                chunk_index=i,
                content=chunk,
            )

            db.add(new_chunk)
            db_chunks.append(new_chunk)

        db.flush()

        # 7. Create Pinecone vectors
        vectors = []

        for chunk, embedding in zip(db_chunks, embeddings):
            vectors.append({
                "id": f"document-{document_id}-chunk-{chunk.id}",
                "values": embedding,
                "metadata": {
                    "document_id": document_id,
                    "chunk_id": chunk.id,
                    "chunk_index": chunk.chunk_index,
                },
            })

        # 8. Upsert new vectors
        index.upsert(vectors=vectors)

        # 9. Commit PostgreSQL
        db.commit()
        db.refresh(document)

        return document

    except HTTPException:
        db.rollback()
        raise

    except Exception:
        db.rollback()

        logger.exception(
            "Failed to update document %s",
            document_id,
        )

        raise HTTPException(
            status_code=500,
            detail="Failed to update document",
        )



@app.post("/documents/upload")
def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported",
        )

    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)

    if file_size > settings.max_file_size:
        raise HTTPException(
            status_code=400,
            detail="File size exceeds the maximum allowed size",
        )


    try:
        reader = PdfReader(file.file)

        if len(reader.pages) > settings.max_pdf_pages:
            raise HTTPException(
                status_code=400,
                detail="PDF exceeds the maximum allowed number of pages",
            )

        text = ""

        for page in reader.pages:
            text += page.extract_text() or ""

        text = text.replace("\x00", "")
        

        if not text.strip():
            raise HTTPException(
                status_code=400,
                detail="The PDF does not contain extractable text",
            )
        
        new_document = Document(
            filename=file.filename,
            content=text,
        )

        db.add(new_document)
        db.flush()

        chunks = chunk_text(text)

        if not chunks:
            raise HTTPException(
                status_code=400,
                detail="The document could not be split into chunks",
            )

        embeddings = create_embeddings(chunks)

        db_chunks = []

        for i, chunk in enumerate(chunks):
            new_chunk = DocumentChunk(
                document_id=new_document.id,
                chunk_index=i,
                content=chunk,
            )

            db.add(new_chunk)
            db_chunks.append(new_chunk)

        db.flush()

        vectors = []

        for chunk, embedding in zip(db_chunks, embeddings):
            vectors.append({
                "id": f"document-{new_document.id}-chunk-{chunk.id}",
                "values": embedding,
                "metadata": {
                    "document_id": new_document.id,
                    "chunk_id": chunk.id,
                    "chunk_index": chunk.chunk_index,
                },
            })

        index.upsert(vectors=vectors)

        db.commit()
        db.refresh(new_document)

        return new_document

    except HTTPException:
        db.rollback()

        raise

    except Exception:
        db.rollback()
        logger.exception("Failed to process document")

        raise HTTPException(
            status_code=500,
            detail="Failed to process document",
        )

@app.get("/search")
def search(
    q: str,
    db: Session = Depends(get_db),
):
    try:
        query_embedding = create_embedding(q)

        return retrieve_chunks(
            query_embedding,
            db,
            top_k=settings.retrieval_top_k,
            score_threshold=settings.retrieval_score_threshold,
        )

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Failed to process search request",
        )


@app.post("/chat", response_model=ChatResponse)
def chat(
    request: ChatRequest,
    db: Session = Depends(get_db),
):
    try:
        route = route_question(request.question)

        if route == "GENERAL":
            answer = generate_response(request.question)

            return {
                "question": request.question,
                "answer": answer,
                "sources": [],
            }

        query_embedding = create_embedding(
            request.question
        )

        chunks = retrieve_chunks(
            query_embedding,
            db,
            top_k=settings.retrieval_top_k,
            score_threshold=settings.retrieval_score_threshold,
            document_ids=request.document_ids,
        )

        answer = generate_rag_response(
            request.question,
            chunks,
        )

        return {
            "question": request.question,
            "answer": answer,
            "sources": build_sources(chunks),
        }

    except Exception as error:
        logger.exception(
            "Failed to process chat request"
        )

        raise HTTPException(
            status_code=500,
            detail=str(error),
        )