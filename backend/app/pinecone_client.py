from pinecone import Pinecone

from .config import settings


pc = Pinecone(
    api_key=settings.pinecone_api_key
)

_index = None


def get_index():
    global _index

    if _index is None:
        _index = pc.Index("ai-knowledge-agent")

    return _index


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

    return get_index().query(**query_kwargs)


def upsert_vectors(vectors):
    get_index().upsert(vectors=vectors)


def delete_document_vectors(document_id: int):
    get_index().delete(
        filter={
            "document_id": document_id,
        }
    )