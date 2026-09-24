from .config import settings
from pinecone import Pinecone

pc = Pinecone(
    api_key=settings.pinecone_api_key
)

index = pc.Index("ai-knowledge-agent")

def search_vectors(
    query_embedding: list[float],
    top_k: int = 5,
    document_ids: list[int] | None = None,
):
    query_kwargs = {
        "vector": query_embedding,
        "top_k": top_k,
        "include_metadata": True,
    }

    if document_ids:
        query_kwargs["filter"] = {
            "document_id": {
                "$in": document_ids
            }
        }

    return index.query(**query_kwargs)


def delete_document_vectors(document_id: int):
    index.delete(
        filter={
            "document_id": document_id,
        }
    )