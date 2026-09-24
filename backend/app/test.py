from .embeddings import create_embeddings
from .pinecone_client import search_vectors
from .database import SessionLocal
from .models import DocumentChunk


query = "What is federated learning?"

embedding = create_embeddings(query)

results = search_vectors(embedding)

chunk_ids = [
    match.metadata["chunk_id"]
    for match in results.matches
]

print("Chunk IDs:", chunk_ids)

db = SessionLocal()

chunks = (
    db.query(DocumentChunk)
    .filter(DocumentChunk.id.in_(chunk_ids))
    .all()
)

for chunk in chunks:
    print("\n---")
    print("Chunk ID:", chunk.id)
    print("Chunk index:", chunk.chunk_index)
    print("Content:")
    print(chunk.content)

db.close()