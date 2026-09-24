from unittest.mock import patch
from unittest.mock import patch, MagicMock
from app.models import Document, DocumentChunk


# ---------------------------------------------------------
# Basic endpoints
# ---------------------------------------------------------

def test_root(client):
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {
        "message": "AI Knowledge Agent API"
    }


def test_health(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


# ---------------------------------------------------------
# Create / Read / List
# ---------------------------------------------------------

def test_create_document(client):
    response = client.post(
        "/documents",
        json={
            "filename": "test.txt",
            "content": "This is a test document.",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["filename"] == "test.txt"
    assert data["content"] == "This is a test document."
    assert "id" in data


def test_get_document(client):
    create_response = client.post(
        "/documents",
        json={
            "filename": "test.txt",
            "content": "Hello world.",
        },
    )

    document_id = create_response.json()["id"]

    response = client.get(
        f"/documents/{document_id}"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == document_id
    assert data["filename"] == "test.txt"
    assert data["content"] == "Hello world."


def test_get_document_not_found(client):
    response = client.get("/documents/999999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Document not found"


def test_get_documents(client):
    client.post(
        "/documents",
        json={
            "filename": "first.txt",
            "content": "First document",
        },
    )

    client.post(
        "/documents",
        json={
            "filename": "second.txt",
            "content": "Second document",
        },
    )

    response = client.get("/documents")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2
    assert data[0]["filename"] == "first.txt"
    assert data[1]["filename"] == "second.txt"


# ---------------------------------------------------------
# Chunks
# ---------------------------------------------------------

def test_get_chunks(client, db):
    document = Document(
        filename="test.txt",
        content="A" * 100,
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

    response = client.get("/chunks")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2
    assert data[0]["chunk_index"] == 0
    assert data[1]["chunk_index"] == 1


# ---------------------------------------------------------
# Update
# ---------------------------------------------------------

@patch("app.main.delete_document_vectors")
@patch("app.main.index.upsert")
@patch("app.main.create_embeddings")
def test_update_document(
    mock_create_embeddings,
    mock_upsert,
    mock_delete_vectors,
    client,
):
    create_response = client.post(
        "/documents",
        json={
            "filename": "old.txt",
            "content": "Old content",
        },
    )

    document_id = create_response.json()["id"]

    mock_create_embeddings.return_value = [
        [0.1] * 384,
    ]

    response = client.put(
        f"/documents/{document_id}",
        json={
            "filename": "new.txt",
            "content": "New content",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == document_id
    assert data["filename"] == "new.txt"
    assert data["content"] == "New content"

    mock_delete_vectors.assert_called_once_with(
        document_id
    )

    mock_upsert.assert_called_once()


def test_update_document_not_found(client):
    response = client.put(
        "/documents/999999",
        json={
            "filename": "new.txt",
            "content": "New content",
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Document not found"


# ---------------------------------------------------------
# Delete
# ---------------------------------------------------------

@patch("app.main.delete_document_vectors")
def test_delete_document(
    mock_delete_vectors,
    client,
):
    create_response = client.post(
        "/documents",
        json={
            "filename": "delete.txt",
            "content": "Delete me",
        },
    )

    document_id = create_response.json()["id"]

    response = client.delete(
        f"/documents/{document_id}"
    )

    assert response.status_code == 200

    assert response.json() == {
        "message": "Document deleted"
    }

    mock_delete_vectors.assert_called_once_with(
        document_id
    )

    get_response = client.get(
        f"/documents/{document_id}"
    )

    assert get_response.status_code == 404


@patch("app.main.delete_document_vectors")
def test_delete_document_not_found(
    mock_delete_vectors,
    client,
):
    response = client.delete(
        "/documents/999999"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Document not found"

    mock_delete_vectors.assert_not_called()


# ---------------------------------------------------------
# PDF upload
# ---------------------------------------------------------

@patch("app.main.PdfReader")
@patch("app.main.index.upsert")
@patch("app.main.create_embeddings")
def test_upload_pdf(
    mock_create_embeddings,
    mock_upsert,
    mock_pdf_reader,
    client,
):
    class FakePage:
        def extract_text(self):
            return "This is extracted PDF content."

    class FakeReader:
        pages = [FakePage()]

    mock_pdf_reader.return_value = FakeReader()

    mock_create_embeddings.return_value = [
        [0.1] * 384,
    ]

    response = client.post(
        "/documents/upload",
        files={
            "file": (
                "test.pdf",
                b"fake pdf content",
                "application/pdf",
            )
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["filename"] == "test.pdf"
    assert data["content"] == (
        "This is extracted PDF content."
    )

    mock_pdf_reader.assert_called_once()
    mock_create_embeddings.assert_called_once()
    mock_upsert.assert_called_once()


def test_upload_rejects_non_pdf(client):
    response = client.post(
        "/documents/upload",
        files={
            "file": (
                "test.txt",
                b"hello",
                "text/plain",
            )
        },
    )

    assert response.status_code == 400

    assert response.json()["detail"] == (
        "Only PDF files are supported"
    )


@patch("app.main.PdfReader")
def test_upload_rejects_empty_pdf(
    mock_pdf_reader,
    client,
):
    class FakePage:
        def extract_text(self):
            return ""

    class FakeReader:
        pages = [FakePage()]

    mock_pdf_reader.return_value = FakeReader()

    response = client.post(
        "/documents/upload",
        files={
            "file": (
                "empty.pdf",
                b"fake pdf",
                "application/pdf",
            )
        },
    )

    assert response.status_code == 400

    assert response.json()["detail"] == (
        "The PDF does not contain extractable text"
    )


# ---------------------------------------------------------
# Search
# ---------------------------------------------------------

@patch("app.main.retrieve_chunks")
@patch("app.main.create_embedding")
def test_search(
    mock_create_embedding,
    mock_retrieve_chunks,
    client,
):
    mock_create_embedding.return_value = [
        0.1
    ] * 384

    mock_retrieve_chunks.return_value = [
        {
            "chunk_id": 10,
            "document_id": 1,
            "chunk_index": 0,
            "score": 0.91,
            "content": "Relevant content",
            "filename": "test.txt",
        }
    ]

    response = client.get(
        "/search",
        params={"q": "What is this document about?"},
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1

    assert data[0]["chunk_id"] == 10
    assert data[0]["document_id"] == 1
    assert data[0]["chunk_index"] == 0
    assert data[0]["score"] == 0.91
    assert data[0]["content"] == "Relevant content"
    assert data[0]["filename"] == "test.txt"

    mock_create_embedding.assert_called_once_with(
        "What is this document about?"
    )


# ---------------------------------------------------------
# Chat / RAG
# ---------------------------------------------------------

@patch("app.main.build_sources")
@patch("app.main.generate_rag_response")
@patch("app.main.retrieve_chunks")
@patch("app.main.create_embedding")
def test_chat(
    mock_create_embedding,
    mock_retrieve_chunks,
    mock_generate_response,
    mock_build_sources,
    client,
):
    mock_create_embedding.return_value = [
        0.1
    ] * 384

    chunks = [
        {
            "chunk_id": 10,
            "document_id": 1,
            "chunk_index": 0,
            "score": 0.95,
            "content": "Relevant information",
            "filename": "test.txt",
        }
    ]

    mock_retrieve_chunks.return_value = chunks

    mock_generate_response.return_value = (
        "The answer is based on the document."
    )

    mock_build_sources.return_value = [
        {
            "document_id": 1,
            "filename": "test.txt",
            "chunk_id": 10,
            "chunk_index": 0,
            "score": 0.95,
        }
    ]

    response = client.post(
        "/chat",
        json={
            "question": "What does the document say?"
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["question"] == (
        "What does the document say?"
    )

    assert data["answer"] == (
        "The answer is based on the document."
    )

    assert len(data["sources"]) == 1

    assert data["sources"][0]["document_id"] == 1
    assert data["sources"][0]["chunk_id"] == 10

    mock_create_embedding.assert_called_once_with(
        "What does the document say?"
    )

    mock_generate_response.assert_called_once_with(
        "What does the document say?",
        chunks,
    )

    mock_build_sources.assert_called_once_with(
        chunks
    )


# ---------------------------------------------------------
# Validation / error cases
# ---------------------------------------------------------

def test_chat_requires_question(client):
    response = client.post(
        "/chat",
        json={},
    )

    assert response.status_code == 422


def test_search_requires_query(client):
    response = client.get("/search")

    assert response.status_code == 422

@patch("app.main.index.upsert")
@patch("app.main.create_embeddings")
@patch("app.main.PdfReader")
def test_upload_pdf_removes_null_characters(
    mock_pdf_reader,
    mock_create_embeddings,
    mock_upsert,
    client,
):
    mock_page = MagicMock()
    mock_page.extract_text.return_value = (
        "This is a PDF\x00 containing\x00 null characters."
    )

    mock_reader = MagicMock()
    mock_reader.pages = [mock_page]
    mock_pdf_reader.return_value = mock_reader

    mock_create_embeddings.return_value = [[0.1] * 384]

    response = client.post(
        "/documents/upload",
        files={
            "file": (
                "test.pdf",
                b"fake pdf content",
                "application/pdf",
            )
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["filename"] == "test.pdf"
    assert "\x00" not in data["content"]
    assert data["content"] == (
        "This is a PDF containing null characters."
    )

    mock_create_embeddings.assert_called_once_with(
        ["This is a PDF containing null characters."]
    )

@patch("app.main.PdfReader")
def test_upload_pdf_with_only_null_characters_is_rejected(
    mock_pdf_reader,
    client,
):
    mock_page = MagicMock()
    mock_page.extract_text.return_value = "\x00\x00\x00"

    mock_reader = MagicMock()
    mock_reader.pages = [mock_page]
    mock_pdf_reader.return_value = mock_reader

    response = client.post(
        "/documents/upload",
        files={
            "file": (
                "empty.pdf",
                b"fake pdf content",
                "application/pdf",
            )
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "The PDF does not contain extractable text"
    )

@patch("app.main.PdfReader")
def test_upload_pdf_with_no_extractable_text_is_rejected(
    mock_pdf_reader,
    client,
):
    mock_page = MagicMock()
    mock_page.extract_text.return_value = None

    mock_reader = MagicMock()
    mock_reader.pages = [mock_page]
    mock_pdf_reader.return_value = mock_reader

    response = client.post(
        "/documents/upload",
        files={
            "file": (
                "image.pdf",
                b"fake pdf content",
                "application/pdf",
            )
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "The PDF does not contain extractable text"
    )