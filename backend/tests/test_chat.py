from unittest.mock import ANY, patch
from app.config import settings


@patch("app.main.generate_rag_response")
@patch("app.main.retrieve_chunks")
@patch("app.main.create_embedding")
def test_chat_success(
    mock_create_embedding,
    mock_retrieve_chunks,
    mock_generate_rag_response,
    client,
):
    mock_create_embedding.return_value = [0.1] * 384

    mock_retrieve_chunks.return_value = [
        {
            "chunk_id": 1,
            "document_id": 1,
            "chunk_index": 0,
            "score": 0.9,
            "content": "Test content",
            "filename": "test.pdf",
        }
    ]

    mock_generate_rag_response.return_value = (
        "This is the answer. [Source 1]"
    )

    response = client.post(
        "/chat",
        json={
            "question": "What is this document about?"
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["question"] == (
        "What is this document about?"
    )

    assert data["answer"] == (
        "This is the answer. [Source 1]"
    )

    mock_create_embedding.assert_called_once_with(
        "What is this document about?"
    )

    mock_retrieve_chunks.assert_called_once()

    call_args = mock_retrieve_chunks.call_args

    assert call_args.args[0] == [0.1] * 384
    assert call_args.kwargs["top_k"] == 5
    assert call_args.kwargs["score_threshold"] == 0.3
    assert call_args.kwargs["document_ids"] == []

    mock_generate_rag_response.assert_called_once_with(
        "What is this document about?",
        mock_retrieve_chunks.return_value,
    )

@patch("app.main.generate_rag_response")
@patch("app.main.retrieve_chunks")
@patch("app.main.create_embedding")
def test_chat_without_results(
    mock_create_embedding,
    mock_retrieve_chunks,
    mock_generate_rag_response,
    client,
):
    mock_create_embedding.return_value = [0.1] * 384
    mock_retrieve_chunks.return_value = []
    mock_generate_rag_response.return_value = (
        "I don't know based on the provided documents."
    )

    response = client.post(
        "/chat",
        json={"question": "What is this?"},
    )

    assert response.status_code == 200

    data = response.json()

    assert data["question"] == "What is this?"
    assert data["answer"] == (
        "I don't know based on the provided documents."
    )
    assert data["sources"] == []

    mock_create_embedding.assert_called_once_with("What is this?")
    mock_generate_rag_response.assert_called_once_with(
        "What is this?",
        [],
    )


@patch(
    "app.main.create_embedding",
    side_effect=Exception("Embedding failed"),
)
def test_chat_handles_embedding_error(
    mock_create_embedding,
    client,
):
    response = client.post(
        "/chat",
        json={"question": "What is this?"},
    )

    assert response.status_code == 500
    assert response.json()["detail"] == "Failed to process chat request"


@patch("app.main.generate_rag_response")
@patch("app.main.retrieve_chunks")
@patch("app.main.create_embedding")
def test_chat_with_document_filter(
    mock_create_embedding,
    mock_retrieve_chunks,
    mock_generate_rag_response,
    client,
):
    mock_create_embedding.return_value = [0.1] * 384

    mock_retrieve_chunks.return_value = []

    mock_generate_rag_response.return_value = (
        "I don't know based on the provided documents."
    )

    response = client.post(
        "/chat",
        json={
            "question": "What is this document about?",
            "document_ids": [42],
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["question"] == (
        "What is this document about?"
    )

    assert data["answer"] == (
        "I don't know based on the provided documents."
    )

    mock_create_embedding.assert_called_once_with(
        "What is this document about?"
    )

    mock_retrieve_chunks.assert_called_once()

    call_args = mock_retrieve_chunks.call_args

    assert call_args.args[0] == [0.1] * 384
    assert call_args.kwargs["top_k"] == 5
    assert call_args.kwargs["score_threshold"] == 0.3
    assert call_args.kwargs["document_ids"] == [42]

    mock_generate_rag_response.assert_called_once_with(
        "What is this document about?",
        mock_retrieve_chunks.return_value,
    )