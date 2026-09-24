from unittest.mock import patch

from app.rag import (
    build_sources,
    generate_rag_response,
)


def test_build_sources():
    chunks = [
        {
            "document_id": 1,
            "filename": "doc1.pdf",
            "chunk_id": 10,
            "chunk_index": 0,
            "score": 0.95,
            "content": "First chunk",
        },
        {
            "document_id": 2,
            "filename": "doc2.pdf",
            "chunk_id": 20,
            "chunk_index": 3,
            "score": 0.82,
            "content": "Second chunk",
        },
    ]

    sources = build_sources(chunks)

    assert sources == [
        {
            "document_id": 1,
            "filename": "doc1.pdf",
            "chunk_id": 10,
            "chunk_index": 0,
            "score": 0.95,
        },
        {
            "document_id": 2,
            "filename": "doc2.pdf",
            "chunk_id": 20,
            "chunk_index": 3,
            "score": 0.82,
        },
    ]


def test_build_sources_empty():
    assert build_sources([]) == []


@patch("app.rag.generate_response")
def test_generate_rag_response(mock_generate_response):
    mock_generate_response.return_value = (
        "The answer is 42."
    )

    chunks = [
        {
            "document_id": 1,
            "filename": "document.pdf",
            "chunk_id": 10,
            "chunk_index": 2,
            "score": 0.91,
            "content": "The answer can be found here.",
        }
    ]

    answer = generate_rag_response(
        "What is the answer?",
        chunks,
    )

    assert answer == "The answer is 42."

    mock_generate_response.assert_called_once()

    prompt = mock_generate_response.call_args.args[0]

    assert "What is the answer?" in prompt
    assert "document.pdf" in prompt
    assert "Chunk: 2" in prompt
    assert "The answer can be found here." in prompt
    assert "[Source 1]" in prompt
    assert "CITATION RULES:" in prompt


@patch("app.rag.generate_response")
def test_generate_rag_response_multiple_chunks(
    mock_generate_response,
):
    mock_generate_response.return_value = "Answer"

    chunks = [
        {
            "document_id": 1,
            "filename": "first.pdf",
            "chunk_id": 10,
            "chunk_index": 0,
            "score": 0.95,
            "content": "First information.",
        },
        {
            "document_id": 2,
            "filename": "second.pdf",
            "chunk_id": 20,
            "chunk_index": 4,
            "score": 0.87,
            "content": "Second information.",
        },
    ]

    generate_rag_response(
        "What do the documents say?",
        chunks,
    )

    prompt = mock_generate_response.call_args.args[0]

    assert "[Source 1]" in prompt
    assert "[Source 2]" in prompt

    assert "first.pdf" in prompt
    assert "second.pdf" in prompt

    assert "First information." in prompt
    assert "Second information." in prompt


@patch("app.rag.generate_response")
def test_generate_rag_response_without_chunks(mock_generate_response):
    answer = generate_rag_response("What is this?", [])

    assert answer == "I don't know based on the provided documents."
    mock_generate_response.assert_not_called()