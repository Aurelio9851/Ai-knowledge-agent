from unittest.mock import Mock, patch

from app.pinecone_client import (
    delete_document_vectors,
    search_vectors,
)


def test_search_vectors():
    fake_result = {
        "matches": [
            {
                "id": "document-1-chunk-1",
                "score": 0.95,
            }
        ]
    }

    mock_index = Mock()
    mock_index.query.return_value = fake_result

    with patch(
        "app.pinecone_client.get_index",
        return_value=mock_index,
    ):

        result = search_vectors(
            query_embedding=[0.1] * 384,
            top_k=5,
        )

    assert result == fake_result

    mock_index.query.assert_called_once_with(
        vector=[0.1] * 384,
        top_k=5,
        include_metadata=True,
    )


def test_delete_document_vectors():
    mock_index = Mock()

    with patch(
        "app.pinecone_client.get_index",
        return_value=mock_index,
    ):

        delete_document_vectors(42)

    mock_index.delete.assert_called_once_with(
        filter={
            "document_id": 42,
        }
    )