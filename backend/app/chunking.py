
from .models import Document, DocumentChunk
from sqlalchemy.orm import Session
from .pinecone_client import search_vectors
from .ollama_client import generate_response



def chunk_text(
    text: str,
    chunk_size: int = 1000,
    overlap: int = 200,
):
    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])

        if end >= len(text):
            break

        start += chunk_size - overlap

    return chunks


def get_chunks_by_ids(
    db: Session,
    chunk_ids: list[int],
):
    return (
        db.query(DocumentChunk)
        .filter(DocumentChunk.id.in_(chunk_ids))
        .all()
    )

def retrieve_chunks(
    query_embedding: list[float],
    db: Session,
    top_k: int = 5,
    score_threshold: float | None = None,
    document_ids: list[int] | None = None,
):
    results = search_vectors(
        query_embedding,
        top_k=top_k,
        document_ids=document_ids,
    )

    matches = [
        match
        for match in results.matches
        if score_threshold is None
        or match.score >= score_threshold
    ]

    chunk_ids = [
        match.metadata["chunk_id"]
        for match in matches
    ]

    if not chunk_ids:
        return []

    chunks = (
        db.query(DocumentChunk, Document)
        .join(
            Document,
            Document.id == DocumentChunk.document_id,
        )
        .filter(DocumentChunk.id.in_(chunk_ids))
        .all()
    )

    chunks_by_id = {
        chunk.id: (chunk, document)
        for chunk, document in chunks
    }

    response = []

    for match in matches:
        chunk, document = chunks_by_id.get(
            match.metadata["chunk_id"],
            (None, None),
        )

        if chunk is not None:
            response.append({
                "chunk_id": chunk.id,
                "document_id": chunk.document_id,
                "chunk_index": chunk.chunk_index,
                "score": match.score,
                "content": chunk.content,
                "filename": document.filename,
            })

    return response


