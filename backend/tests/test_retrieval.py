from unittest.mock import patch
from unittest.mock import MagicMock, patch
from app.models import Document, DocumentChunk
from app.chunking import retrieve_chunks


def test_retrieve_chunks(client, db):
    document = Document(
        filename="test.txt",
        content="Test document content",
    )

    db.add(document)
    db.commit()
    db.refresh(document)

    chunk = DocumentChunk(
        document_id=document.id,
        chunk_index=0,
        content="This is the relevant chunk.",
    )

    db.add(chunk)
    db.commit()
    db.refresh(chunk)

    pinecone_result = type(
        "PineconeResult",
        (),
        {
            "matches": [
                type(
                    "Match",
                    (),
                    {
                        "score": 0.95,
                        "metadata": {
                            "chunk_id": chunk.id,
                        },
                    },
                )()
            ]
        },
    )()

    with patch(
        "app.chunking.search_vectors",
        return_value=pinecone_result,
    ) as mock_search:

        results = retrieve_chunks(
            query_embedding=[0.1] * 384,
            db=db,
            top_k=5,
        )

    assert len(results) == 1

    result = results[0]

    assert result["chunk_id"] == chunk.id
    assert result["document_id"] == document.id
    assert result["chunk_index"] == 0
    assert result["score"] == 0.95
    assert result["content"] == "This is the relevant chunk."
    assert result["filename"] == "test.txt"

    mock_search.assert_called_once_with(
        [0.1] * 384,
        top_k=5,
        document_ids=None,
    )


def test_retrieve_chunks_applies_score_threshold(db):
    document = Document(
        filename="test.txt",
        content="Test document",
    )

    db.add(document)
    db.commit()
    db.refresh(document)

    chunk = DocumentChunk(
        document_id=document.id,
        chunk_index=0,
        content="Low relevance chunk",
    )

    db.add(chunk)
    db.commit()
    db.refresh(chunk)

    pinecone_result = type(
        "PineconeResult",
        (),
        {
            "matches": [
                type(
                    "Match",
                    (),
                    {
                        "score": 0.50,
                        "metadata": {
                            "chunk_id": chunk.id,
                        },
                    },
                )()
            ]
        },
    )()

    with patch(
        "app.chunking.search_vectors",
        return_value=pinecone_result,
    ):

        results = retrieve_chunks(
            query_embedding=[0.1] * 384,
            db=db,
            top_k=5,
            score_threshold=0.7,
        )

    assert results == []


def test_retrieve_chunks_keeps_results_above_threshold(db):
    document = Document(
        filename="test.txt",
        content="Test document",
    )

    db.add(document)
    db.commit()
    db.refresh(document)

    chunk = DocumentChunk(
        document_id=document.id,
        chunk_index=0,
        content="Relevant chunk",
    )

    db.add(chunk)
    db.commit()
    db.refresh(chunk)

    pinecone_result = type(
        "PineconeResult",
        (),
        {
            "matches": [
                type(
                    "Match",
                    (),
                    {
                        "score": 0.85,
                        "metadata": {
                            "chunk_id": chunk.id,
                        },
                    },
                )()
            ]
        },
    )()

    with patch(
        "app.chunking.search_vectors",
        return_value=pinecone_result,
    ):

        results = retrieve_chunks(
            query_embedding=[0.1] * 384,
            db=db,
            top_k=5,
            score_threshold=0.7,
        )

    assert len(results) == 1
    assert results[0]["score"] == 0.85


def test_retrieve_chunks_without_results(db):
    pinecone_result = type(
        "PineconeResult",
        (),
        {
            "matches": [],
        },
    )()

    with patch(
        "app.chunking.search_vectors",
        return_value=pinecone_result,
    ):

        results = retrieve_chunks(
            query_embedding=[0.1] * 384,
            db=db,
            top_k=5,
        )

    assert results == []


def test_retrieve_chunks_ignores_missing_database_chunks(db):
    pinecone_result = type(
        "PineconeResult",
        (),
        {
            "matches": [
                type(
                    "Match",
                    (),
                    {
                        "score": 0.95,
                        "metadata": {
                            "chunk_id": 999999,
                        },
                    },
                )()
            ]
        },
    )()

    with patch(
        "app.chunking.search_vectors",
        return_value=pinecone_result,
    ):

        results = retrieve_chunks(
            query_embedding=[0.1] * 384,
            db=db,
            top_k=5,
        )

    assert results == []


def test_retrieve_chunks_preserves_pinecone_order(db):
    document = Document(
        filename="test.txt",
        content="Test document",
    )

    db.add(document)
    db.commit()
    db.refresh(document)

    chunk_1 = DocumentChunk(
        document_id=document.id,
        chunk_index=0,
        content="First chunk",
    )

    chunk_2 = DocumentChunk(
        document_id=document.id,
        chunk_index=1,
        content="Second chunk",
    )

    db.add_all([chunk_1, chunk_2])
    db.commit()
    db.refresh(chunk_1)
    db.refresh(chunk_2)

    pinecone_result = type(
        "PineconeResult",
        (),
        {
            "matches": [
                type(
                    "Match",
                    (),
                    {
                        "score": 0.95,
                        "metadata": {
                            "chunk_id": chunk_2.id,
                        },
                    },
                )(),
                type(
                    "Match",
                    (),
                    {
                        "score": 0.80,
                        "metadata": {
                            "chunk_id": chunk_1.id,
                        },
                    },
                )(),
            ]
        },
    )()

    with patch(
        "app.chunking.search_vectors",
        return_value=pinecone_result,
    ):

        results = retrieve_chunks(
            query_embedding=[0.1] * 384,
            db=db,
            top_k=5,
        )

    assert len(results) == 2

    assert results[0]["chunk_id"] == chunk_2.id
    assert results[0]["score"] == 0.95

    assert results[1]["chunk_id"] == chunk_1.id
    assert results[1]["score"] == 0.80

@patch("app.chunking.search_vectors")
def test_retrieve_chunks_with_document_filter(
    mock_search_vectors,
    db,
):
    mock_match = MagicMock()
    mock_match.metadata = {
        "chunk_id": 1,
    }
    mock_match.score = 0.9

    mock_results = MagicMock()
    mock_results.matches = [mock_match]

    mock_search_vectors.return_value = mock_results

    document = Document(
        filename="test.pdf",
        content="Test document",
    )

    db.add(document)
    db.commit()
    db.refresh(document)

    chunk = DocumentChunk(
        document_id=document.id,
        chunk_index=0,
        content="Test content",
    )

    db.add(chunk)
    db.commit()
    db.refresh(chunk)

    mock_match.metadata["chunk_id"] = chunk.id

    result = retrieve_chunks(
        [0.1] * 384,
        db,
        top_k=5,
        score_threshold=0.5,
        document_ids=[document.id],
    )

    assert len(result) == 1
    assert result[0]["document_id"] == document.id

    mock_search_vectors.assert_called_once_with(
        [0.1] * 384,
        top_k=5,
        document_ids=[document.id],
    )