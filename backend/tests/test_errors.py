from unittest.mock import patch

from app.models import Document


@patch(
    "app.main.delete_document_vectors",
    side_effect=Exception("Pinecone unavailable"),
)
def test_delete_rolls_back_when_pinecone_fails(
    mock_delete,
    client,
    db,
):
    document = Document(
        filename="test.txt",
        content="Important content",
    )

    db.add(document)
    db.commit()
    db.refresh(document)

    document_id = document.id

    response = client.delete(
        f"/documents/{document_id}"
    )

    assert response.status_code == 500

    assert response.json()["detail"] == (
        "Failed to delete document"
    )

    mock_delete.assert_called_once_with(
        document_id
    )

    document = (
        db.query(Document)
        .filter(Document.id == document_id)
        .first()
    )

    assert document is not None
    assert document.filename == "test.txt"


@patch(
    "app.main.delete_document_vectors",
    side_effect=Exception("Pinecone unavailable"),
)
def test_update_rolls_back_when_pinecone_delete_fails(
    mock_delete,
    client,
    db,
):
    document = Document(
        filename="original.txt",
        content="Original content",
    )

    db.add(document)
    db.commit()
    db.refresh(document)

    document_id = document.id

    response = client.put(
        f"/documents/{document_id}",
        json={
            "filename": "updated.txt",
            "content": "Updated content",
        },
    )

    assert response.status_code == 500

    assert response.json()["detail"] == (
        "Failed to update document"
    )

    document = (
        db.query(Document)
        .filter(Document.id == document_id)
        .first()
    )

    assert document.filename == "original.txt"
    assert document.content == "Original content"

@patch(
    "app.main.delete_document_vectors",
    side_effect=Exception("Pinecone unavailable"),
)
def test_update_rolls_back_when_pinecone_delete_fails(
    mock_delete,
    client,
    db,
):
    document = Document(
        filename="original.txt",
        content="Original content",
    )

    db.add(document)
    db.commit()
    db.refresh(document)

    document_id = document.id

    response = client.put(
        f"/documents/{document_id}",
        json={
            "filename": "updated.txt",
            "content": "Updated content",
        },
    )

    assert response.status_code == 500

    assert response.json()["detail"] == (
        "Failed to update document"
    )

    document = (
        db.query(Document)
        .filter(Document.id == document_id)
        .first()
    )

    assert document.filename == "original.txt"
    assert document.content == "Original content"

@patch("app.main.create_embeddings")
@patch("app.main.PdfReader")
def test_upload_rolls_back_when_embedding_fails(
    mock_pdf_reader,
    mock_embeddings,
    client,
    db,
):
    class FakePage:
        def extract_text(self):
            return "PDF content"

    class FakeReader:
        pages = [FakePage()]

    mock_pdf_reader.return_value = FakeReader()

    mock_embeddings.side_effect = Exception(
        "Embedding failed"
    )

    response = client.post(
        "/documents/upload",
        files={
            "file": (
                "test.pdf",
                b"fake pdf",
                "application/pdf",
            )
        },
    )

    assert response.status_code == 500

    assert (
        db.query(Document).count()
        == 0
    )

@patch("app.main.create_embeddings")
@patch("app.main.PdfReader")
def test_upload_rolls_back_when_embedding_fails(
    mock_pdf_reader,
    mock_embeddings,
    client,
    db,
):
    class FakePage:
        def extract_text(self):
            return "PDF content"

    class FakeReader:
        pages = [FakePage()]

    mock_pdf_reader.return_value = FakeReader()

    mock_embeddings.side_effect = Exception(
        "Embedding failed"
    )

    response = client.post(
        "/documents/upload",
        files={
            "file": (
                "test.pdf",
                b"fake pdf",
                "application/pdf",
            )
        },
    )

    assert response.status_code == 500

    assert (
        db.query(Document).count()
        == 0
    )


from unittest.mock import patch

from app.config import settings


@patch("app.main.PdfReader")
def test_upload_rejects_file_too_large(
    mock_pdf_reader,
    client,
):
    oversized_content = b"x" * (
        settings.max_file_size + 1
    )

    response = client.post(
        "/documents/upload",
        files={
            "file": (
                "large.pdf",
                oversized_content,
                "application/pdf",
            )
        },
    )

    assert response.status_code == 400

    assert response.json()["detail"] == (
        "File size exceeds the maximum allowed size"
    )

    mock_pdf_reader.assert_not_called()




@patch("app.main.PdfReader")
def test_upload_rejects_too_many_pages(
    mock_pdf_reader,
    client,
):
    class FakeReader:
        pages = [object()] * (
            settings.max_pdf_pages + 1
        )

    mock_pdf_reader.return_value = FakeReader()

    response = client.post(
        "/documents/upload",
        files={
            "file": (
                "large.pdf",
                b"fake pdf",
                "application/pdf",
            )
        },
    )

    assert response.status_code == 400

    assert response.json()["detail"] == (
        "PDF exceeds the maximum allowed number of pages"
    )

@patch(
    "app.main.PdfReader",
    side_effect=Exception("Invalid PDF"),
)
def test_upload_handles_pdf_parser_error(
    mock_pdf_reader,
    client,
):
    response = client.post(
        "/documents/upload",
        files={
            "file": (
                "broken.pdf",
                b"not a real pdf",
                "application/pdf",
            )
        },
    )

    assert response.status_code == 500

    assert response.json()["detail"] == (
        "Failed to process document"
    )


@patch(
    "app.main.create_embedding",
    side_effect=Exception("Embedding failed"),
)
def test_search_handles_embedding_error(
    mock_create_embedding,
    client,
):
    response = client.get(
        "/search",
        params={"q": "What is this?"},
    )

    assert response.status_code == 500
    assert response.json()["detail"] == "Failed to process search request"